import pathlib
import os
from XmlReader import *
from screener import *


if __name__ == '__main__':
    print("SDN Screener started.")
    data_store = DataStore()
    screener = Screener(db=data_store)
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
