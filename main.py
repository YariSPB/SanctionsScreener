import pathlib
import os
from XmlReader import *
from screener import *
from Exporter import *
import sqlite3


if __name__ == '__main__':
    print("SDN Screener started.")
    #print(sqlite3.)
    #xml_r = XmlReader()
    #resu = xml_r.find_by_value('1053300906900')

    #distinct_parties = xml_r.get_distinct_entities()
    #persons = xml_r.get_all_SDN_persons()
    data_store = DataStore()
    sdn_service = Screener(data_store)
    sdn_service.get_new_SDN()
    #data_store.insert_sdn_persons(xml_r.SDN_Persons)
    #data_store.insert_new(distinct_parties)
    #sdn_persons = data_store.get_SDN_persons()
    #exporter = Exporter(data_store)
    #export_sdn_persons = exporter.export_sdn_csv()
    ss=5
    exit()


    #main
    data_store = DataStore()
    screener = Screener(db=data_store)
    screener.get_new_SDN()

    #data_store.export_sdn_csv()
    exit()

    #xml_r = XmlReader()
    #distinct_parties = xml_r.get_distinct_entities()
    #data_store.insert_new(distinct_parties)
    #exit()

    if not screener.new_SDN_published():
        print('No new SDN entries. Terminating')
        exit()

    screener.load_SDN_file(c.raw_xml_name)
#    if not os.path.isfile(curr_dir + raw_data_dir + '/' + raw_xml_name):
#        print("No xml file: " + '/' + raw_xml_name)
#        exit()

    xml_r = XmlReader()
    distinct_parties = xml_r.get_distinct_entities()
    data_store.insert_new(distinct_parties)
    data_store.export_sdn_csv()
