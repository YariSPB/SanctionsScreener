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
        self.__setup_property_table()
        self.__setup_feature_table()
        self.__setup_identity_tb()
        self.__setup_person_tb()
        self.__setup_SDN_tb()
        self.__setup_alias_tb()
        self.commit()

    def export_sdn_csv(self):
        data = self.cur.execute("SELECT * FROM SDNParty").fetchall()
        try:
            with open(c.curr_dir + c.export_dir + "/" + c.SDN_SCV, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                header = [ \
                    'FixedRef', \
                    'PrimaryName', \
                    'EntityType', \
                    'SDNStatus', \
                    'SDNEntryDate', \
                    'SDNPrograms', \
                    'Alias']
                writer.writerow(header)
                for item in data:
                    line = [item[0], \
                            item[1], \
                            c.get_entity_str(item[2]), \
                            'Yes' if item[3] == 1 else 'No', \
                            item[4], \
                            item[5],
                            item[6]]
                    writer.writerow(line)
        except Exception as e:
            print(str(e))
            exit()

    def print_sdn_csv(self):
        #sdn_id_tpl = self.cur.execute('SELECT id FROM SDN').fetchall()
        #sdn_id = []
        #for tpl in sdn_id_tpl:
         #   sdn_id.append(tpl[0])

        query = '''SELECT s.id,
                      s.entry_date,
                      s.program,
                      s.identity_id,
                      i.name,
                      i.type,
                      p.gender,
                      p.birth_date,
                      p.nationality,
                      p.tax_id
                   FROM SDN s
                   INNER JOIN Identity i
                      ON i.id = s.identity_id
                   INNER JOIN Person p
                      ON p.identity_id = s.identity_id;
                '''
        data = self.cur.execute(query).fetchall()

        identity_ids = []
        for tpl in data:
            identity_ids.append(str(tpl[3]))
        identity_ids_str = ', '.join(identity_ids)

        alias_query = f'''SELECT a.id, a.name, a.script
                         FROM Alias a
                         WHERE a.identity_id IN ({identity_ids_str});
                      '''
        aliases = self.cur.execute(alias_query).fetchall()
        b= 6

        try:
            with open(c.curr_dir + c.export_dir + "/" + c.SDN_SCV, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                header = [ \
                    'FixedRef', \
                    'SDNEntryDate', \
                    'SDNProgram', \
                    'PrimaryName', \
                    'EntityType', \
                    'Gender',
                     'BirthDate',
                     'Nationality',
                     'TaxID',
                    'Comment']
                writer.writerow(header)
                for item in data:
                    comment = []
                    if item[6]:
                        comment.append(f'Gender {item[6]}')
                    if item[7]:
                        comment.append(f'BirthDate {item[7]}')
                    if item[8]:
                        comment.append(f'Nationality {item[8]}')
                    if item[9]:
                        comment.append(f'TaxID {item[9]}')
                    line = [item[0], \
                            item[1], \
                            item[2], \
                            item[4], \
                            item[5],
                            item[6],
                            item[7],
                            item[8],
                            item[9],
                            '; '.join(comment)]
                    writer.writerow(line)
        except Exception as e:
            print(str(e))
            exit()

    #self.__compile_comment(item)

    def get_latest_entry_date(self):
        db_entry = self.cur.execute('SELECT MAX(SDNEntryDate) FROM SDNParty')
        result = db_entry.fetchone()
        if result[0]:
            print('Latest Database SDN entry from: ' + result[0])
            return result[0]
        return None

    def insert_new(self, distinct_parties):
        for key in distinct_parties:
            self.__insert_entity(distinct_parties[key])
        self.con.commit()

    def __insert_entity(self, entity):
        insert_command = '''INSERT OR IGNORE INTO SDNParty (
                       FixedRef, 
                       PrimaryName,
                       EntityType,
                       SDNStatus,
                       SDNEntryDate,
                       SDNPrograms,
                       AliasLatin)
                       VALUES (?,?,?,?,?,?,?)
                       '''

        data_tuple = (entity['FixedRef'], \
                      entity['PrimaryName'], \
                      entity['EntityType'].value, \
                      1, \
                      entity['SDNEntryDate'], \
                      entity['SDNPrograms'], \
                      entity['AliasLatin'])
        self.con.execute(insert_command, data_tuple)

    def __insert_feature(self, entity):

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
                       SDNPrograms TEXT,
                       AliasLatin TEXT
                       )''')
        con.commit()
        con.close()

    def __setup_property_table(self):
        # query = self.cur.execute("SELECT name FROM sqlite_master WHERE name = 'Properties'")
        # if not query.fetchone()[0]:
        self.cur.execute('CREATE TABLE IF NOT EXISTS Properties (' + c.properties_schema + ')')
        self.con.commit()

        for prop in c.properties:
            query = 'SELECT property_id, name FROM Properties WHERE name = "{}"'.format(prop)
            db_entry = self.cur.execute(query)
            if not db_entry.fetchone():
                push = 'INSERT INTO Properties (name) VALUES ("{}")'.format(prop)
                self.cur.execute(push)
                self.con.commit()

    def __setup_feature_table(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Features (' + c.features_schema + ')')
        # self.con.commit()

    def __setup_identity_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Identity (' + c.identity_schema + ')')
        # self.con.commit()

    def __setup_person_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Person (' + c.person_schema + ')')
        # self.con.commit()

    def __setup_SDN_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS SDN (' + c.sdn_schema + ')')
        # self.con.commit()

    def __setup_alias_tb(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS Alias (' + c.alias_schema + ')')
        # self.con.commit()

    def commit(self):
        self.con.commit()

    def insert_sdn_persons(self, persons):
        for key in persons:
            self.insert_sdn_person(persons[key])
        self.commit()

    def insert_sdn_person(self, sdn_person):
        if not sdn_person:
            return
        record = self.cur.execute(f'SELECT id FROM SDN WHERE id = {sdn_person.sdn_id}')
        if record.fetchone():
            return
        record = self.cur.execute(f'SELECT id FROM Identity WHERE name = "{sdn_person.person.primary_name}"')
        if record.fetchone():
            return

        query = "INSERT INTO Identity (name) VALUES (?)"
        push = 'INSERT INTO Identity (name,type) VALUES (?,?)'
        p_tuple = (sdn_person.person.primary_name, 'Person')
        self.cur.execute(push, p_tuple)
        identity_id = self.cur.lastrowid

        person_query = '''INSERT INTO Person (
                       identity_id, 
                       gender,
                       birth_date,
                       nationality,
                       tax_id)
                       VALUES (?,?,?,?,?)
                       '''

        person_data = (identity_id, \
                       sdn_person.person.gender, \
                       sdn_person.person.birth_date, \
                       sdn_person.person.nationality, \
                       sdn_person.person.tax_id, \
                       )
        self.con.execute(person_query, person_data)

        sdn_query = '''INSERT INTO SDN (
                       id,
                       identity_id, 
                       entry_date,
                       program)
                       VALUES (?,?,?,?)
                       '''

        sdn_data = (sdn_person.sdn_id,
                    identity_id,
                    sdn_person.date,
                    sdn_person.programs
                    )
        self.con.execute(sdn_query, sdn_data)

        for alias in sdn_person.person.secondary_latin:
            alias_query = '''INSERT INTO Alias (
                           identity_id, 
                           name,
                           script)
                           VALUES (?,?,?)
                           '''

            alias_data = (identity_id, alias, 'latin')
            self.cur.execute(alias_query, alias_data)

        for alias in sdn_person.person.secondary_cyrillic:
            alias_query = '''INSERT INTO Alias (
                           identity_id, 
                           name,
                           script)
                           VALUES (?,?,?)
                           '''

            alias_data = (identity_id, alias, 'cyrillic')
            self.cur.execute(alias_query, alias_data)
