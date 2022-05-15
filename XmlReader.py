import xml.etree.ElementTree as ET
import config as c
from entities import *

tax_id_ref = '1596'

class XmlReader:
    def __init__(self):
        self.tree = ET.parse(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name)
        self.root = self.tree.getroot()
        self.all_parties = {}
        self.SDN_persons = {}
        self.countries = {}
        self.IDRegDocTypes = {}

    def find_by_value(self, str):
        value = self.root.findall(f".//*[.='{str}']")
        return value

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

    def __append_person(self, entry):
        person = Person()
        fixed_ref = entry.attrib.get('FixedRef')
        profile = entry.find(c.tree_prefix + 'Profile')
        identity = profile.find(c.tree_prefix + 'Identity')
        identity_id = identity.attrib.get('ID')
        person.tax_id = self.__get_reg_id(identity_id)
        aliases = identity.findall(c.tree_prefix + 'Alias')
        alias_dict = self.__get__aliases(aliases)
        person.primary_name = alias_dict['Primary']
        person.secondary_latin = alias_dict['Secondary_latin']
        person.secondary_cyrillic = alias_dict['Secondary_cyrillic']

        features = profile.findall(c.tree_prefix + 'Feature')
        for feature in features:
            if feature.attrib.get('FeatureTypeID') == '8':
                #get DOB
                feature_version = feature.find(c.tree_prefix + 'FeatureVersion')
                date_period = feature_version.find(c.tree_prefix + 'DatePeriod')
                start_date = date_period.find(c.tree_prefix + 'Start')
                from_date = start_date.find(c.tree_prefix + 'From')

                year = from_date.find(c.tree_prefix + 'Year').text
                month = from_date.find(c.tree_prefix + 'Month').text.zfill(2)
                day = from_date.find(c.tree_prefix + 'Day').text.zfill(2)
                person.birth_date = year + '-' + month + '-' + day
            elif feature.attrib.get('FeatureTypeID') == '224':
                #gender
                feature_version = feature.find(c.tree_prefix + 'FeatureVersion')
                version_detail = feature_version.find(c.tree_prefix + 'VersionDetail')
                if version_detail.attrib.get('DetailReferenceID') == '91526':
                    person.gender = 'Male'
                elif version_detail.attrib.get('DetailReferenceID') == '91527':
                    person.gender = 'Female'
            elif feature.attrib.get('FeatureTypeID') == '10':
                #nationality country
                feature_version = feature.find(c.tree_prefix + 'FeatureVersion')
                version_detail = feature_version.find(c.tree_prefix + 'VersionDetail')
                if version_detail.attrib.get('DetailTypeID') == '1433':
                    #country only
                    version_location = feature_version.find(c.tree_prefix + 'VersionLocation')
                    location_id = version_location.attrib.get('LocationID')
                    person.nationality = self.__get_nationality(location_id)

        #if person.tax_id:
        #    print (person.tax_id)
        self.SDN_persons[fixed_ref] = person

    def __get_reg_id(self, identity_id):
        reg_records = self.root.findall(f"{c.tree_prefix}IDRegDocuments/{c.tree_prefix}IDRegDocument[@IdentityID='{identity_id}']")
        if not reg_records:
            return None
        return reg_records[0].find(f"{c.tree_prefix}IDRegistrationNo").text


    def __get_reg_data(self, identity_id):
        reg_records = self.root.findall(f"{c.tree_prefix}IDRegDocuments/{c.tree_prefix}IDRegDocument[@IdentityID='{identity_id}']") # and @IDRegDocTypeID='{tax_id_ref}']")
        if not reg_records:
            return None
        records = {}
        for record in reg_records:
            IDRegDocTypeID = record.attrib.get('IDRegDocTypeID')
            registration_type = self.IDRegDocTypes.get(IDRegDocTypeID)
            if not registration_type:
                registration_type = self.root.find(f"{c.tree_prefix}ReferenceValueSets/{c.tree_prefix}IDRegDocTypeValues/{c.tree_prefix}IDRegDocType[@ID='{IDRegDocTypeID}']").text
                self.IDRegDocTypes[IDRegDocTypeID] = registration_type
            IDRegistrationDoc = record.find(f"{c.tree_prefix}IDRegistrationNo").text
            records[registration_type] = IDRegistrationDoc
        return records



    def __get_nationality(self, location_id):
        if location_id in self.countries:
            return self.countries[location_id]
        locations = self.root.find(f"{c.tree_prefix}Locations")
        location = locations.find(f"{c.tree_prefix}Location[@ID='{location_id}']")
        value = location.find(f".//{c.tree_prefix}Value").text
        self.countries[location_id] = value
        return value


    def __get__aliases(self, alias_nodes):
        aliases = {"Primary": None, "Secondary_latin": [], "Secondary_cyrillic": []}
        for alias in alias_nodes:
            name_temp = []
            for documented_name in alias:
                for documented_name_part in documented_name:
                    for name_part in documented_name_part:
                        if name_part.attrib.get('ScriptID') == "215":
                            script = 'Latin'
                        elif name_part.attrib.get('ScriptID') == "220":
                            script = 'Cyrillic'
                        else:
                            script = 'Else'
                        name_temp.append(name_part.text)

            if alias.attrib.get('Primary') == 'false':
                if script == 'Cyrillic':
                    aliases["Secondary_cyrillic"].append(' '.join(name_temp))
                elif script == 'Latin':
                    aliases["Secondary_latin"].append(' '.join(name_temp))
            else:
                aliases['Primary'] = ' '.join(name_temp)

        return aliases

    def __get_full_name(self, name_container):
        full_name = []
        for name_part_holder in name_container:
            # name_part = name_part_holder.find(c.tree_prefix + 'NamePartValue').text
            full_name.append(name_part_holder.find(c.tree_prefix + 'NamePartValue').text)
        return ' '.join(full_name)

    def __append_sanctions_data(self):
        sanction_entries = self.root.find(c.tree_prefix + 'SanctionsEntries')
        for sanctions_entry in sanction_entries:
            entry_event = sanctions_entry.find(c.tree_prefix + 'EntryEvent')
            if entry_event.attrib.get('EntryEventTypeID') == '1':
                FixedRef = sanctions_entry.attrib.get('ProfileID')
                # if self.all_parties[FixedRef] in self.all_parties:
                date_record = entry_event.find(c.tree_prefix + 'Date')
                year = date_record.find(c.tree_prefix + 'Year').text
                month = date_record.find(c.tree_prefix + 'Month').text.zfill(2)
                day = date_record.find(c.tree_prefix + 'Day').text.zfill(2)
                self.all_parties[FixedRef]['SDNEntryDate'] = year + '-' + month + '-' + day

            sanctions_measures = sanctions_entry.findall(c.tree_prefix + 'SanctionsMeasure')
            programs = None
            for measure in sanctions_measures:
                if measure.attrib.get('SanctionsTypeID') == '1':
                    if not programs:
                        programs = measure.find(c.tree_prefix + 'Comment').text
                    else:
                        programs += ', ' + measure.find(c.tree_prefix + 'Comment').text
            self.all_parties[FixedRef]["SDNPrograms"] = programs
