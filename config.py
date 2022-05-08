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
export_dir = '/export'
SDN_DB_name = "SDN.db"
SDN_SCV = 'SDN.csv'
tree_prefix = '{http://www.un.org/sanctions/1.0}'


class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5


def get_entity_str(number):
    return Entity(number).name
