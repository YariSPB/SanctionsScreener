import os
import sqlite3
import config as c
import pathlib

class DataStore:
    def __init__(self):
        pathlib.Path(c.curr_dir + c.db_dir).mkdir(exist_ok=True)
        if not os.path.isfile(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name):
            self.__create_SDN_DB()
        self.con = sqlite3.connect(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name)
        self.cur = self.con.cursor()

    def get_latest_entry_date(self):
        db_entry = self.cur.execute('SELECT MAX(SDNEntryDate) FROM SDNParty')
        result = db_entry.fetchone()
        if result[0]:
            print('Latest Database SDN entry from: ' + result[0])
            return result[0]
        return None

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
        con = sqlite3.connect(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name)
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
