import ftplib
import pathlib
import os
import sqlite3
import xml.etree.ElementTree as ET
from enum import Enum
from XmlReader import *


HOSTNAME = "ofacftp.treas.gov"
FOLDER_NAME = "/fac_delim"
USERNAME = "anonymous"
PASSWORD = "anonymous@domain.com"
curr_dir = os.getcwd()
raw_data_dir = '/raw_data'
raw_xml_name = '/sdn_advanced.xml'
db_dir = '/database'
SDN_DB_name = "SDN.db"
tree_prefix = '{http://www.un.org/sanctions/1.0}'


class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def load_file(filename):
    # Connect FTP Server
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # force UTF-8 encoding
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(FOLDER_NAME)
    ftp_server.dir()

    # Enter File Name with Extension
    #filename = "sdn_advanced.xml"

    # Write file in binary mode
    with open(curr_dir + raw_data_dir +"/"+filename, "wb") as file:
        # Command for Downloading the file "RETR filename"
       ftp_server.retrbinary(f"RETR {filename}", file.write)

    # Close the Connection
    ftp_server.quit()


def create_SDN_DB():
    con = sqlite3.connect(curr_dir + db_dir+"/" + SDN_DB_name)
    cur = con.cursor()
    # Create table
    cur.execute('''CREATE TABLE IF NOT EXISTS DistinctParty
                   (FixedRef INTEGER PRIMARY KEY, 
                   PrimaryName TEXT,
                   EntityType INTEGER,
                   SDN INTEGER
                   )''')
    con.commit()
    con.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    #curr_dir = os.getcwd()
    #raw_data_dir = '/raw_data'
    pathlib.Path(curr_dir + raw_data_dir).mkdir(exist_ok=True)
    pathlib.Path(curr_dir + db_dir).mkdir(exist_ok=True)

    if not os.path.isfile(curr_dir + db_dir +"/" + SDN_DB_name):
        create_SDN_DB()

    if not os.path.isfile(curr_dir + raw_data_dir +raw_xml_name):
        print("No xml file: " +raw_xml_name)
        exit()

    xml_r = XmlReader()

    distinct_parties = xml_r.get_distinct_entities()


#    tree = ET.parse(curr_dir + raw_data_dir +raw_xml_name)
#    root = tree.getroot()
#    print(root)


#    distinct_parties = root.find(tree_prefix + 'DistinctParties')
#    print(distinct_parties)
#    count = 0

#    all_parties = {}


#    for entry in distinct_parties:
#        party_dict = {}
#        print(entry.tag, entry.attrib)
#        fixed_ref = entry.attrib.get('FixedRef')
#        party_dict['FixedRef'] = entry.attrib.get('FixedRef')

#        profile = entry.find(tree_prefix + 'Profile')
#        print(profile.tag)
#       entity_type = None
#       entity_sub_type = profile.attrib.get('PartySubTypeID')
#        if entity_sub_type == '4':
#            entity_type = Entity.INDIVIDUAL
#        elif entity_sub_type == '3':
#            entity_type = Entity.ENTITY
#        elif entity_sub_type == '2':
#            entity_type = Entity.AIRCRAFT
#        elif entity_sub_type == '1':
#            entity_type = Entity.VESSEL
#        else:
#            entity_type = Entity.OTHER

#        party_dict['EntityType'] = entity_type


#        identity = profile.find(tree_prefix + 'Identity')
#        aliases = identity.findall(tree_prefix + 'Alias')
#        primary_alias = None
#        for alias in aliases:
#            if alias.attrib.get('Primary') == 'true':
#                primary_alias = alias
#                break

#        latin_name_container = None
#        for name_type in primary_alias:
#            if name_type.attrib.get('DocNameStatusID') == '1':
#                latin_name_container = name_type
#                break

#        full_name = ''
#        for name_part_holder in latin_name_container:
#           name_part = name_part_holder.find(tree_prefix + 'NamePartValue').text
#            full_name = full_name + name_part

#        party_dict['PrimaryName'] = full_name
#        all_parties[fixed_ref] = party_dict
#        #party_dict['SDN'] = 1

#        print(full_name)
#        count = count+1
#        if count > 50:
#            break
#    print(count)

    #entity_record = """INSERT INTO DistinctParty
    #    (FixedRef,PrimaryName,EntityType,SDN)
    #    VALUES(fixed_ref,full_name,entity_type,1)"""

    #cursor = conn.cursor()
    #cursor.execute(employee, (eid, name, email, phone, date))
    #conn.commit()


    x=5



    #load_file('add.csv')
