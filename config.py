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


class Script(Enum):
    latin = 1,
    cyrillic = 2



class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5


def get_entity_str(number):
    return Entity(number).name


# Database schemas
properties = [
    'Date_birth',
    'Nationality',
    'Alias_latin',
    'Alias_cyrillic',
    'Tax_ID'
]

identity_schema = '''id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 type TEXT NOT NULL
              '''

person_schema = '''id INTEGER PRIMARY KEY,
                   identity_id  INTEGER NOT NULL,
                   gender TEXT,
                   birth_date TEXT,
                   nationality TEXT,
                   tax_id TEXT,
                   FOREIGN KEY (identity_id) REFERENCES Identity (id)             
                '''

sdn_schema = '''id INTEGER PRIMARY KEY,
                identity_id  INTEGER NOT NULL,
                entry_date TEXT,
                program TEXT,
                FOREIGN KEY (identity_id) REFERENCES Identity (id)
             '''

alias_schema = '''id INTEGER PRIMARY KEY,
                  identity_id  INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  script TEXT,
                  FOREIGN KEY (identity_id) REFERENCES Identity (id)
'''

