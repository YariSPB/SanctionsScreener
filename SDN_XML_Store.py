import xml.etree.ElementTree as ET
import config as c
from entities import *

tax_id_ref = '1596'
p = c.tree_prefix


class SDN_XML_Store:
    def __init__(self):
        self.tree = ET.parse(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name)
        self.root = self.tree.getroot()
        self.SDN_data = {}
        self.__collect_SDN_data()
        self.IDRegDocTypes = {}
        self.reg_data = {}
        self.__get_all_reg_data()
        self.areas = {}
        self.countries_all = {}
        self.__load_all_counties()
        self.__load_loc_areas()
        self.locations = {}
        self.__load_locations()

    def __collect_SDN_data(self):
        sanction_entries = self.root.find(f'{p}SanctionsEntries')
        for sanctions_entry in sanction_entries:
            sdn_data = self.__get_SDN_data(sanctions_entry)
            self.SDN_data[sdn_data['FixedRef']] = sdn_data

    def __get_SDN_data(self, sanctions_entry):
        SDN_data = {}
        entry_event = sanctions_entry.find(c.tree_prefix + 'EntryEvent')
        if entry_event.attrib.get('EntryEventTypeID') == '1':
            SDN_data['FixedRef'] = sanctions_entry.attrib.get('ProfileID')
            date_record = entry_event.find(f'{p}Date')
            year = date_record.find(f'{p}Year').text
            month = date_record.find(f'{p}Month').text.zfill(2)
            day = date_record.find(f'{p}Day').text.zfill(2)
            SDN_data['SDNEntryDate'] = year + '-' + month + '-' + day

        sanctions_measures = sanctions_entry.findall(f'{p}SanctionsMeasure')
        programs = None
        for measure in sanctions_measures:
            if measure.attrib.get('SanctionsTypeID') == '1':
                if not programs:
                    programs = measure.find(f'{p}Comment').text
                else:
                    programs += ', ' + measure.find(f'{p}Comment').text
        SDN_data["SDNPrograms"] = programs
        return SDN_data

    def __get_all_reg_data(self):
        IDREgDocuments = self.root.find(p + 'IDRegDocuments')
        for reg_doc in IDREgDocuments:
            identity = reg_doc.attrib.get('IdentityID')
            if identity not in self.reg_data:
                self.reg_data[identity] = []
            IDRegDocTypeID = reg_doc.attrib.get('IDRegDocTypeID')
            registration_type = self.IDRegDocTypes.get(IDRegDocTypeID)
            if not registration_type:
                registration_type = self.root.find(
                    f"{p}ReferenceValueSets/{p}IDRegDocTypeValues/{p}IDRegDocType[@ID='{IDRegDocTypeID}']").text
                self.IDRegDocTypes[IDRegDocTypeID] = registration_type
            IDRegistrationDoc = reg_doc.find(f"{p}IDRegistrationNo").text
            self.reg_data[identity].append((registration_type, IDRegistrationDoc))

    def __load_loc_areas(self):
        locations = self.root.findall(
            f"{p}ReferenceValueSets/{p}AreaCodeValues/{p}AreaCode")
        for location in locations:
            countryID = location.attrib.get('CountryID')
            location = location.attrib.get('Description')
            self.areas[countryID] = location

    def __load_locations(self):
        locations = self.root.findall(f"{p}Locations/{p}Location")
        for location in locations:
            id = location.attrib.get('ID')
            if not id in self.locations:
                self.locations[id] = {}
            loc_area_code = location.find(f"{p}LocationAreaCode")
            if loc_area_code is not None:
                area_code = loc_area_code.attrib.get('AreaCodeID')
                self.locations[id]['AreaCode'] = area_code
            #value = location.find(f".//{c.tree_prefix}Value")
            #if value is not None:
            #    self.locations[id]['Nationality'] = value.text

    def __load_all_counties(self):
        countries = self.root.findall(
            f"{p}ReferenceValueSets/{p}CountryValues/{p}Country")
        for country in countries:
            countryID = country.attrib.get('ID')
            name = country.text
            self.countries_all[countryID] = name
