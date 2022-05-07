import os
from enum import Enum

HOSTNAME = "ofacftp.treas.gov"
FOLDER_NAME = "/fac_delim"
USERNAME = "anonymous"
PASSWORD = "anonymous@domain.com"
curr_dir = os.getcwd()
raw_data_dir = '/raw_data'
raw_xml_name = 'sdn_advanced.xml'
db_dir = '/database'
SDN_DB_name = "SDN.db"
tree_prefix = '{http://www.un.org/sanctions/1.0}'


class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5