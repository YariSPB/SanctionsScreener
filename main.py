import pathlib
import os
from XmlReader import *
from screener import *
from Exporter import *
import sqlite3


if __name__ == '__main__':
    print("SDN Screener started.")
    xml_reader = XmlReader()
    xml_reader.load_all_SDN_persons()
    data_store = DataStore()
    data_store.insert_sdn_persons(xml_reader.SDN_Persons)
    exp = Exporter(data_store)
    exp.export_sdn_csv()
    #sdn_service = Screener(data_store)
    #sdn_service.get_new_SDN()

    ss=5
    exit()



    if not screener.new_SDN_published():
        print('No new SDN entries. Terminating')
        exit()

