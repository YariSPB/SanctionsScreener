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


# Database schemas
properties_schema = '''property_id INTEGER PRIMARY KEY, 
                name TEXT
             '''
properties = [
    'Date_birth',
    'Nationality',
    'Alias_latin',
    'Alias_cyrillic',
    'Tax_ID'
]

features_schema = '''feature_id INTEGER PRIMARY KEY,
                Value TEXT,
                Entity_ref INTEGER NOT NULL,
                Property_ref INTEGER NOT NULL,
                FOREIGN KEY (Entity_ref) REFERENCES SDNParty (FixedRef)
                ON DELETE CASCADE
                FOREIGN KEY (Property_ref) REFERENCES Properties (property_id)
                ON DELETE CASCADE
                UNIQUE(Value, Entity_ref, Property_ref)
             '''



