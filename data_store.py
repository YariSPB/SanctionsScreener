import os
import sqlite3
from enum import Enum

db_dir = '/database'
SDN_DB_name = "SDN.db"
curr_dir = os.getcwd()


class Entity(Enum):
    INDIVIDUAL = 1
    ENTITY = 2
    VESSEL = 3
    AIRCRAFT = 4
    OTHER = 5


class DataStore:
    def __init__(self):
        if not os.path.isfile(curr_dir + db_dir + "/" + SDN_DB_name):
            self.__create_SDN_DB()
        self.con = sqlite3.connect(curr_dir + db_dir + "/" + SDN_DB_name)

    def insert_new(self, distinct_parties):
        cur = self.con.cursor()
        insert_command = '''INSERT INTO SDNParty (
                       FixedRef, 
                       PrimaryName,
                       EntityType,
                       SDNStatus,
                       SDNEntryDate,
                       SDNPrograms)
                       VALUES (?,?,?,?,?,?)
                       '''

        for key in distinct_parties:
            not_exist_check = 'SELECT 1 FROM SDNParty WHERE FixedRef = {}'.format(key)
            db_entry = cur.execute(not_exist_check)

            if not db_entry.fetchone():
                data_tuple = (key, \
                              distinct_parties[key]['PrimaryName'], \
                              distinct_parties[key]['EntityType'].value, \
                              1, \
                              distinct_parties[key]['SDNEntryDate'], \
                              distinct_parties[key]['SDNPrograms'])
                self.con.execute(insert_command, data_tuple)
        self.con.commit()
        pass


    def __create_SDN_DB(self):
        con = sqlite3.connect(curr_dir + db_dir + "/" + SDN_DB_name)
        cur = con.cursor()
        # Create table
        cur.execute('''CREATE TABLE IF NOT EXISTS SDNParty
                       (FixedRef INTEGER PRIMARY KEY, 
                       PrimaryName TEXT,
                       EntityType INTEGER,
                       SDNStatus INTEGER,
                       SDNEntryDate TEXT,
                       SDNPrograms TEXT
                       )''')
        con.commit()
        con.close()
