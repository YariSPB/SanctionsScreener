import os
import sqlite3
import config as c
import pathlib
import csv


class DataStore:
    def __init__(self):
        pathlib.Path(c.curr_dir + c.db_dir).mkdir(exist_ok=True)
        pathlib.Path(c.curr_dir + c.export_dir).mkdir(exist_ok=True)

        if not os.path.isfile(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name):
            self.__create_SDN_DB()
        self.con = sqlite3.connect(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name)
        self.cur = self.con.cursor()

    def export_sdn_csv(self):
        data = self.cur.execute("SELECT * FROM SDNParty").fetchall()
        try:
            with open(c.curr_dir + c.export_dir + "/" + c.SDN_SCV, 'w', newline='') as f:
                writer = csv.writer(f)
                header = [ \
                    'FixedRef', \
                    'PrimaryName', \
                    'EntityType', \
                    'SDNStatus', \
                    'SDNEntryDate', \
                    'SDNPrograms']
                writer.writerow(header)
                for item in data:
                    line = [item[0],\
                            item[1],\
                            c.get_entity_str(item[2]),\
                            'Yes' if item[3] == 1 else 'No',\
                            item[4],\
                            item[5]]
                    writer.writerow(line)
        except Exception as e:
            print(str(e))
            exit()

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
