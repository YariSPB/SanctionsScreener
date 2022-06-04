import encodings.utf_8
from data_store import *
import config as c
import pathlib
import csv, codecs
import io
import re


file_path = c.curr_dir + c.export_dir + "/" + c.SDN_SCV


class Exporter:
    def __init__(self, db: DataStore):
        pathlib.Path(c.curr_dir + c.export_dir).mkdir(exist_ok=True)
        self.data_store = db

    def export_sdn_entities(self, entity_dict):
        export_sdn = []
        for key in entity_dict:
            export_sdn.append(Export_SDN_Entity(entity_dict[key]))

        print('Saving to CSV')
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                header = ['SDN_Code',
                          'Name_Cyrillic',
                          'Name_Latin',
                          'Type',
                          'Comment',
                          'Issue_Date']
                writer.writerow(header)
                for item in export_sdn:

                    line = item.get_line()
                    #print(line)
                    writer.writerow(line)
        except Exception as e:
            print(str(e))
            exit()
        return

    def export_sdn_csv(self):
        sdn_persons = self.data_store.get_SDN_persons()
        export_sdn_persons = []
        for key in sdn_persons:
            export_sdn_persons.append(Export_SDN_Person(sdn_persons[key]))

        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                header = ['SDN_Code',
                          'Name_Cyrillic',
                          'Name_Latin',
                          'Type',
                          'Comment',
                          'Issue_Date']
                writer.writerow(header)
                for item in export_sdn_persons:
                    # if item.cyrillic_name:
                    # print(item.cyrillic_name)
                    line = [item.sdn_id,
                            item.cyrillic_name,
                            item.latin_name,
                            'Person',
                            item.comment,
                            item.issue_date]
                    writer.writerow(line)
        except Exception as e:
            print(str(e))
            exit()
        return

class Export_SDN_Entity:
    def __init__(self, sdn_entity: SDN_Entity):
        if sdn_entity.unique_id == '26744':
            f=5
        self.sdn_id = sdn_entity.unique_id
        self.cyrillic_name = sdn_entity.get_cyrillic_name()
        if self.cyrillic_name:
            self.cyrillic_name = self.__filter_cyrillic(self.cyrillic_name)
            #self.cyrillic_name.encode('utf-8', 'ignore').decode()
        self.latin_name = sdn_entity.primary_name
        self.type = 'Entity'
        self.comment = None
        self.issue_date = sdn_entity.SDN_issue_date
        self.__get_comment(sdn_entity)

    def __filter_cyrillic(self, str):
        allowed = '[^аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОпПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ 0-9\,\.\-\"]'
        replace_w = '_'
        return re.sub(allowed, replace_w, str)

        for alias in self.aliases:
            if alias[1] == c.Script.cyrillic.name:
                return alias[0]

    def __get_comment(self, sdn_entity: SDN_Entity):
        comment=[]
        comment.append(f'Programs {sdn_entity.SDN_programs}')

        if sdn_entity.reg_date:
            comment.append(f'Reg.Date {sdn_entity.reg_date}')

        if sdn_entity.reg_data:
            for record in sdn_entity.reg_data:
                comment.append(f'{record[0]} {record[1]}')

        if len(sdn_entity.locations) > 0:
            for location in sdn_entity.locations:
                full_address = location.print()
                clean_address = full_address.encode('ascii', errors='ignore').decode()
                if len(clean_address) > 0:
                   comment.append(f'Address {clean_address}')

        for alias in sdn_entity.aliases:
            if alias[1] == c.Script.cyrillic.name:
                # remove unreadable
                #cyrillic_name = alias[0].encode('utf-8', 'ignore').decode()
                cyrillic_name = self.__filter_cyrillic(alias[0])
                record = f"a.k.a. {cyrillic_name}"
            else:
                # only ascii for latin
                record = f"a.k.a. {alias[0].encode('ascii',errors='ignore').decode()}"
            comment.append(record)
        self.comment = '; '.join(comment)

    def get_line(self):
        line = [self.sdn_id,
                self.cyrillic_name,
                self.latin_name,
                self.type,
                self.comment,
                self.issue_date]
        return line

class Export_SDN_Person:
    def __init__(self, sdn_person: SDN_Person):
        self.sdn_id = sdn_person.sdn_id
        self.cyrillic_name = sdn_person.person.get_cyrillic_name()
        if self.cyrillic_name:
            self.cyrillic_name.encode('utf-8', 'ignore')
        self.latin_name = sdn_person.person.primary_name
        self.tax_id = sdn_person.person.tax_id
        self.__get_comment(sdn_person)
        self.issue_date = sdn_person.date

    def __get_comment(self, sdn_person):
        comment=[]
        comment.append(f'Program {sdn_person.programs}')

        if sdn_person.person.gender:
            comment.append(f'Gender {sdn_person.person.gender}')
        if sdn_person.person.birth_date:
            comment.append(f'BirthDate {sdn_person.person.birth_date}')
        if sdn_person.person.nationality:
            comment.append(f'Nationality {sdn_person.person.nationality}')

        for alias in sdn_person.person.aliases:
            if alias[1] == c.Script.cyrillic.name:
                # remove unreadable
                cyrillic_name = alias[0].encode('utf-8', 'ignore').decode()
                record = f"a.k.a. {cyrillic_name}"
            else:
                # only ascii for latin
                record = f"a.k.a. {alias[0].encode('ascii',errors='ignore').decode()}"
            comment.append(record)
        self.comment = '; '.join(comment)
