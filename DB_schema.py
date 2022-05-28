
import os
import sqlite3
import config as c
import pathlib
from entities import *


class DB_schema:
    def __init__(self):
        pathlib.Path(c.curr_dir + c.db_dir).mkdir(exist_ok=True)
        self.con = sqlite3.connect(c.curr_dir + c.db_dir + "/" + c.SDN_DB_name)
        self.cur = self.con.cursor()
        self.__setup_identity_tb()
        self.__setup_person_tb()
        self.__setup_SDN_tb()
        self.__setup_alias_tb()
        self.con.commit()


    def __setup_identity_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Identity (' + identity_schema + ')')
        # self.con.commit()

    def __setup_person_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Person (' + person_schema + ')')
        # self.con.commit()

    def __setup_SDN_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS SDN (' + sdn_schema + ')')

    def __setup_alias_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Alias (' + alias_schema + ')')



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