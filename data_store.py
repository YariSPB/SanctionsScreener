import os
import sqlite3
import config as c
import pathlib
from entities import *
from DB_schema import DB_schema


class DataStore(DB_schema):
    def __init__(self):
        DB_schema.__init__(self)
        pass

    def get_SDN_persons(self):
        sdn_persons = {}
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
        persons_list = self.cur.execute(query).fetchall()

        for record in persons_list:
            person = Person()
            person.primary_name = record[4]
            person.gender = record[6]
            person.birth_date = record[7]
            person.nationality = record[8]
            person.tax_id = record[9]
            person.unique_id = record[3]
            sdn_person = SDN_Person(person, record[0], record[1], record[2])
            sdn_persons[record[3]] = sdn_person


        identity_ids = []
        for tpl in persons_list:
            identity_ids.append(str(tpl[3]))
        identity_ids_str = ', '.join(identity_ids)

        alias_query = f'''SELECT a.id, a.identity_id, a.name, a.script
                         FROM Alias a
                         WHERE a.identity_id IN ({identity_ids_str});
                      '''
        aliases = self.cur.execute(alias_query).fetchall()

        for alias in aliases:
            tpl = (alias[2], alias[3])
            sdn_persons[alias[1]].person.aliases.append(tpl)
        return sdn_persons

    def get_latest_sdnperson_date(self):
        db_entry = self.cur.execute('SELECT MAX(entry_date) FROM SDN')
        result = db_entry.fetchone()
        if result[0]:
            print('Latest Database SDN record is from: ' + result[0])
            return result[0]
        return None

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
