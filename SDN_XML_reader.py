import xml.etree.ElementTree as ET
import config as c
from entities import *
from SDN_XML_Store import SDN_XML_Store
import time

#tax_id_ref = '1596'
p = c.tree_prefix


class SDN_XML_reader(SDN_XML_Store):
    def __init__(self):
        SDN_XML_Store.__init__(self)
        self.persons = {}
        self.all_SDN = {}
        self.SDN_Persons = {}
        self.SDN_Entities = {}
        self.countries = {}

    def get_issue_date(self):
        date_of_issue = self.root.find(f'{p}DateOfIssue')
        year = date_of_issue.find(f'{p}Year').text
        month = date_of_issue.find(f'{p}Month').text.zfill(2)
        day = date_of_issue.find(f'{p}Day').text.zfill(2)
        issue_date_str = year + '-' + month + '-' + day
        return time.strptime(issue_date_str, "%Y-%m-%d")

    def find_by_value(self, str):
        value = self.root.findall(f".//*[.='{str}']")
        return value

    def get_all_SDN(self):
        distinct_parties = self.root.find(f'{p}DistinctParties')
        for entry in distinct_parties:
            fixed_ref = entry.attrib.get('FixedRef')
            profile = entry.find(f'{p}Profile')
            entity_sub_type = profile.attrib.get('PartySubTypeID')
            if entity_sub_type == '4':
                sdn_entity = self.__get_SDN_person(entry)
                self.SDN_Persons[fixed_ref] = sdn_entity
            elif entity_sub_type == '3':
                sdn_entity = self.__get_generic_SDN_entity(entry, c.Entity.ENTITY)
                self.SDN_Entities[fixed_ref] = sdn_entity
            elif entity_sub_type == '2':
                sdn_entity = self.__get_generic_SDN_entity(entry, c.Entity.AIRCRAFT)
                self.SDN_Entities[fixed_ref] = sdn_entity
            elif entity_sub_type == '1':
                sdn_entity = self.__get_generic_SDN_entity(entry, c.Entity.VESSEL)
                self.SDN_Entities[fixed_ref] = sdn_entity
            else:
                sdn_entity = self.__get_generic_SDN_entity(entry, c.Entity.OTHER)
                self.SDN_Entities[fixed_ref] = sdn_entity
            self.all_SDN[fixed_ref] = sdn_entity
        return self.all_SDN

    def __get_generic_SDN_entity(self, entry, entity_type: c. Entity):
        entity = SDN_Entity(entity_type)
        entity.type = entity_type
        entity.unique_id = entry.attrib.get('FixedRef')
        profile = entry.find(f'{p}Profile')
        identity = profile.find(f'{p}Identity')
        identity_id = identity.attrib.get('ID')
        if identity_id in self.reg_data:
            entity.reg_data = self.reg_data[identity_id]
        entity.primary_name = self.__get_primary_name(identity)
        entity.aliases = self.__get_secondary_aliases(identity)
        features = profile.findall(c.tree_prefix + 'Feature')
        # collect entity specific features
        for feature in features:
            # collect locations
            if feature.attrib.get('FeatureTypeID') == '25':
                feature_version = feature.find(f'{p}FeatureVersion')
                version_location = feature_version.find(f'{p}VersionLocation')
                location_id = version_location.attrib.get('LocationID')
                loc = self.locations[location_id]
                entity.locations.add(loc)

        sanctions_record = self.SDN_data[entity.unique_id]
        entity.SDN_issue_date = sanctions_record['SDNEntryDate']
        entity.SDN_programs = sanctions_record['SDNPrograms']
        return entity

    def __get_SDN_person(self, entry):
        person = Person()
        fixed_ref = entry.attrib.get('FixedRef')
        profile = entry.find(f'{p}Profile')
        identity = profile.find(f'{p}Identity')
        identity_id = identity.attrib.get('ID')
        person.tax_id = self.__get_person_reg_id(identity_id)
        alias_dict = self.__get__aliases(identity)
        person.primary_name = alias_dict['Primary']
        person.secondary_latin = alias_dict['Secondary_latin']
        person.secondary_cyrillic = alias_dict['Secondary_cyrillic']
        person.aliases = self.__get_secondary_aliases(identity)
        features = profile.findall(f'{p}Feature')
        for feature in features:
            if feature.attrib.get('FeatureTypeID') == '8':
                # get DOB
                from_date = feature.find(f"{p}FeatureVersion/{p}DatePeriod/{p}Start/{p}From")
                year = from_date.find(f'{p}Year').text
                month = from_date.find(f'{p}Month').text.zfill(2)
                day = from_date.find(f'{p}Day').text.zfill(2)
                person.birth_date = year + '-' + month + '-' + day
            elif feature.attrib.get('FeatureTypeID') == '224':
                # gender
                version_detail = feature.find(f"{p}FeatureVersion/{p}VersionDetail")
                if version_detail.attrib.get('DetailReferenceID') == '91526':
                    person.gender = 'Male'
                elif version_detail.attrib.get('DetailReferenceID') == '91527':
                    person.gender = 'Female'
            elif feature.attrib.get('FeatureTypeID') == '10':
                # nationality country
                feature_version = feature.find(f'{p}FeatureVersion')
                version_detail = feature_version.find(f'{p}VersionDetail')
                if version_detail.attrib.get('DetailTypeID') == '1433':
                    # country only
                    version_location = feature_version.find(f'{p}VersionLocation')
                    location_id = version_location.attrib.get('LocationID')
                    person.nationality = self.__get_nationality(location_id)

        sdn_record = self.SDN_data[fixed_ref]
        return SDN_Person(person, fixed_ref, sdn_record['SDNEntryDate'], sdn_record['SDNPrograms'])


    def __get_person_reg_id(self, identity_id):
        if identity_id in self.reg_data:
            return self.reg_data[identity_id][0][1]
        return None

    def __get_nationality(self, location_id):
        if location_id in self.countries:
            return self.countries[location_id]
        locations = self.root.find(f"{p}Locations")
        location = locations.find(f"{p}Location[@ID='{location_id}']")
        value = location.find(f".//{p}Value").text
        self.countries[location_id] = value
        return value

    def __get_primary_name(self, identity):
        primary_documented_name = identity.find(f".//{p}DocumentedName[@DocNameStatusID='1']")
        primary = []
        for documented_name_part in primary_documented_name:
            for name_part in documented_name_part:
                primary.append(name_part.text)
        return ' '.join(primary)

    def __get_secondary_aliases(self,identity):
        aliases = []
        for alias in identity.findall(p + 'Alias'):
            for documented_name in alias:
                fullname_latin = []
                fullname_cyrillic = []
                #search only secondary == 2
                if documented_name.attrib.get('DocNameStatusID') == '2':
                    for documented_name_part in documented_name:
                        for name_part in documented_name_part:
                            if name_part.attrib.get('ScriptID') == "215":
                                fullname_latin.append(name_part.text)
                            elif name_part.attrib.get('ScriptID') == "220":
                                fullname_cyrillic.append(name_part.text)
                    if fullname_latin:
                        name = ' '.join(fullname_latin)
                        aliases.append((name, c.Script.latin.name))
                    elif fullname_cyrillic:
                        name = ' '.join(fullname_cyrillic)
                        aliases.append((name, c.Script.cyrillic.name))
        return aliases


    def __get__aliases(self, identity):
        aliases = {"Primary": None, "Secondary_latin": [], "Secondary_cyrillic": []}
        primary_documented_name = identity.find(f".//{p}DocumentedName[@DocNameStatusID='1']")
        primary = []
        for documented_name_part in primary_documented_name:
            for name_part in documented_name_part:
                primary.append(name_part.text)
        aliases['Primary'] = ' '.join(primary)

        for alias in identity.findall(p + 'Alias'):
            for documented_name in alias:
                fullname_latin = []
                fullname_cyrillic = []
                if documented_name.attrib.get('DocNameStatusID') == '2':
                    for documented_name_part in documented_name:
                        for name_part in documented_name_part:
                            if name_part.attrib.get('ScriptID') == "215":
                                fullname_latin.append(name_part.text)
                            elif name_part.attrib.get('ScriptID') == "220":
                                fullname_cyrillic.append(name_part.text)
                    if fullname_latin:
                        aliases["Secondary_latin"].append(' '.join(fullname_latin))
                    elif fullname_cyrillic:
                        aliases["Secondary_cyrillic"].append(' '.join(fullname_cyrillic))
        return aliases
