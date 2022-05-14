import xml.etree.ElementTree as ET
import config as c


class XmlReader:
    def __init__(self):
        self.tree = ET.parse(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name)
        self.root = self.tree.getroot()
        self.all_parties = {}

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

            full_name = None
            for name_part_holder in latin_name_container:
                name_part = name_part_holder.find(c.tree_prefix + 'NamePartValue').text
                if not full_name:
                    full_name = name_part
                else:
                    full_name += ' ' + name_part

            party_dict['PrimaryName'] = full_name

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
