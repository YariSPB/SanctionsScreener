import xml.etree.ElementTree as ET
import config as c
from entities import *
from SDN_XML_Store import SDN_XML_Store

tax_id_ref = '1596'
p = c.tree_prefix


class XmlReader(SDN_XML_Store):
    def __init__(self):
        SDN_XML_Store.__init__(self)
        self.persons = {}
        self.all_SDN = {}
        self.SDN_Persons = {}
        self.SDN_Entities = {}
        self.countries = {}
        #self.__load_all_SDN_persons()
        #self.__load_SDN_entities()

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
                self.all_SDN[fixed_ref] = sdn_entity
            elif entity_sub_type == '3':
                sdn_entity = self.__get_SDN_entity(entry)
                self.SDN_Entities[fixed_ref] = sdn_entity
                self.all_SDN[fixed_ref] = sdn_entity
            elif entity_sub_type == '2':
                entity_type = c.Entity.AIRCRAFT
            elif entity_sub_type == '1':
                entity_type = c.Entity.VESSEL
            else:
                entity_type = c.Entity.OTHER
        return self.all_SDN

    def get_distinct_entities(self):
        distinct_parties = self.root.find(c.tree_prefix + 'DistinctParties')
        for entry in distinct_parties:
            party_dict = {}
            fixed_ref = entry.attrib.get('FixedRef')
            party_dict['FixedRef'] = entry.attrib.get('FixedRef')

            profile = entry.find(c.tree_prefix + 'Profile')
            entity_sub_type = profile.attrib.get('PartySubTypeID')
            if entity_sub_type == '4':
                entity_type = c.Entity.INDIVIDUAL
                self.__append_person(entry)
            elif entity_sub_type == '3':
                entity_type = c.Entity.ENTITY
            elif entity_sub_type == '2':
                entity_type = c.Entity.AIRCRAFT
            elif entity_sub_type == '1':
                entity_type = c.Entity.VESSEL
            else:
                entity_type = c.Entity.OTHER

            party_dict['EntityType'] = entity_type
            identity = profile.find(c.tree_prefix + 'Identity')
            aliases = identity.findall(c.tree_prefix + 'Alias')
            alias_dict = self.__get__aliases(aliases)
            party_dict['PrimaryName'] = alias_dict['Primary']

            # get latin aliases concatenated
            second_name = []
            for alias in aliases:
                if alias.attrib.get('Primary') == 'false':
                    for documented_name in alias:
                        if documented_name.attrib.get('DocNameStatusID') == '2':
                            for documented_name_part in documented_name:
                                for name_part in documented_name_part:
                                    if name_part.attrib.get('ScriptID') == "215":
                                        second_name.append(name_part.text)
                    break

            party_dict['AliasLatin'] = ' '.join(second_name)
            party_dict['Alias_dict'] = alias_dict

            self.all_parties[fixed_ref] = party_dict
        self.__append_sanctions_data()
        return self.all_parties

    def __load_all_SDN_persons(self):
        self.find_persons()
        # self.__collect_SDN_data()
        for key in self.persons:
            sdn_record = self.SDN_data[key]
            person = self.persons[key]
            sdn_person = SDN_Person(person, key, sdn_record['SDNEntryDate'], sdn_record['SDNPrograms'])
            self.SDN_Persons[key] = sdn_person
        pass

    def __load_SDN_entities(self):
        distinct_parties = self.root.find(f'{p}DistinctParties')
        for entry in distinct_parties:
            profile = entry.find(f'{p}Profile')
            entity_sub_type = profile.attrib.get('PartySubTypeID')
            if entity_sub_type == '3':
                sdn_entity = self.__get_SDN_entity(entry)
                self.SDN_Entities[sdn_entity.unique_id] = sdn_entity

    def __get_SDN_entity(self, entry):
        entity = SDN_Entity()
        entity.unique_id = entry.attrib.get('FixedRef')
        profile = entry.find(f'{p}Profile')
        identity = profile.find(f'{p}Identity')
        identity_id = identity.attrib.get('ID')
        if identity_id in self.reg_data:
            entity.reg_data = self.reg_data[identity_id]
        alias_dict = self.__get__aliases(identity)
        entity.primary_name = alias_dict['Primary']
        #entity.aliases = alias_dict['Secondary_latin'] + alias_dict['Secondary_cyrillic']
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
                #area = self.locations[location_id].area#['Area']
                #entity.locations.add(area)

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


    def find_persons(self):
        distinct_parties = self.root.find(f'{p}DistinctParties')
        for entry in distinct_parties:
            party_dict = {}
            fixed_ref = entry.attrib.get('FixedRef')
            party_dict['FixedRef'] = entry.attrib.get('FixedRef')
            profile = entry.find(c.tree_prefix + 'Profile')
            entity_sub_type = profile.attrib.get('PartySubTypeID')
            if entity_sub_type == '4':
                entity_type = c.Entity.INDIVIDUAL
                self.__append_person(entry)

    def __append_person(self, entry):
        person = Person()
        fixed_ref = entry.attrib.get('FixedRef')
        profile = entry.find(f'{p}Profile')
        identity = profile.find(f'{p}Identity')
        identity_id = identity.attrib.get('ID')
        # person.tax_id = self.__get_reg_id(identity_id)
        person.tax_id = self.__get_person_reg_id(identity_id)
        # aliases = identity.findall(c.tree_prefix + 'Alias')
        alias_dict = self.__get__aliases(identity)
        person.primary_name = alias_dict['Primary']
        person.secondary_latin = alias_dict['Secondary_latin']
        person.secondary_cyrillic = alias_dict['Secondary_cyrillic']

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

        self.persons[fixed_ref] = person

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
