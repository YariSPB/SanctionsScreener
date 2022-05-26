import config as c


class Person:
    def __init__(self):
        self.primary_name = None
        self.gender = None
        self.secondary_latin = []
        self.secondary_cyrillic = []
        self.birth_date = None
        self.nationality = None
        self.tax_id = None
        self.aliases = []
        self.unique_id = None

    def get_cyrillic_name(self):
        for alias in self.aliases:
            if alias[1] == c.Script.cyrillic.name:
                return alias[0]


class SDN_Person:
    def __init__(self, parent, fix_id, date, programs):
        self.person = parent
        self.sdn_id = fix_id
        self.date = date
        self.programs = programs


