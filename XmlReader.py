import xml.etree.ElementTree as ET
import os
from enum import Enum

curr_dir = os.getcwd()
raw_data_dir = '/raw_data'
raw_xml_name = '/sdn_advanced.xml'
tree_prefix = '{http://www.un.org/sanctions/1.0}'


class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5


class XmlReader:
    def __init__(self):
        self.tree = ET.parse(curr_dir + raw_data_dir + raw_xml_name)
        self.root = self.tree.getroot()
        self.all_parties = {}

    def get_distinct_entities(self):
        distinct_parties = self.root.find(tree_prefix + 'DistinctParties')
        #all_parties = {}

        for entry in distinct_parties:
            party_dict = {}
            #print(entry.tag, entry.attrib)
            fixed_ref = entry.attrib.get('FixedRef')
            party_dict['FixedRef'] = entry.attrib.get('FixedRef')

            profile = entry.find(tree_prefix + 'Profile')
            #print(profile.tag)
            entity_type = None
            entity_sub_type = profile.attrib.get('PartySubTypeID')
            if entity_sub_type == '4':
                entity_type = Entity.INDIVIDUAL
            elif entity_sub_type == '3':
                entity_type = Entity.ENTITY
            elif entity_sub_type == '2':
                entity_type = Entity.AIRCRAFT
            elif entity_sub_type == '1':
                entity_type = Entity.VESSEL
            else:
                entity_type = Entity.OTHER

            party_dict['EntityType'] = entity_type

            identity = profile.find(tree_prefix + 'Identity')
            aliases = identity.findall(tree_prefix + 'Alias')
            primary_alias = None
            for alias in aliases:
                if alias.attrib.get('Primary') == 'true':
                    primary_alias = alias
                    break

            latin_name_container = None
            for name_type in primary_alias:
                if name_type.attrib.get('DocNameStatusID') == '1':
                    latin_name_container = name_type
                    break

            full_name = ''
            for name_part_holder in latin_name_container:
                name_part = name_part_holder.find(tree_prefix + 'NamePartValue').text
                full_name = full_name + name_part

            party_dict['PrimaryName'] = full_name
            self.all_parties[fixed_ref] = party_dict

        self.__append_sanctions_data()

        return self.all_parties


    def __append_sanctions_data(self):
        sanction_entries = self.root.find(tree_prefix + 'SanctionsEntries')

        for sanctions_entry in sanction_entries:
            entry_event = sanctions_entry.find(tree_prefix + 'EntryEvent')
            if entry_event.attrib.get('EntryEventTypeID') == '1':
                FixedRef = sanctions_entry.attrib.get('ProfileID')
                #if self.all_parties[FixedRef] in self.all_parties:
                date_record = entry_event.find(tree_prefix + 'Date')
                year = date_record.find(tree_prefix + 'Year').text
                month = date_record.find(tree_prefix + 'Month').text
                day = date_record.find(tree_prefix + 'Day').text
                self.all_parties[FixedRef]["Date"] = year+'-'+month+'-'+day
                r = 5

            sanctions_measures = sanctions_entry.findall(tree_prefix + 'SanctionsMeasure')
            programs = ''
            for measure in sanctions_measures:
                if measure.attrib.get('SanctionsTypeID') == '1':
                    programs += measure.find(tree_prefix + 'Comment').text
            self.all_parties[FixedRef]["SanctionsPrograms"] = programs