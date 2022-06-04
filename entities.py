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


class SDN_Entity:
    def __init__(self):
        self.unique_id = None
        self.primary_name = None
        self.aliases = []
        self.reg_date = None
        self.reg_data = []
        self.locations = set()
        self.SDN_issue_date = None
        self.SDN_programs = []

    def get_cyrillic_name(self):
        for alias in self.aliases:
            if alias[1] == c.Script.cyrillic.name:
                return alias[0]


class Location:
    def __init__(self, location_id):
        self.id = location_id
        self.area = None
        self.country = None
        self.region = None
        self.state_province = None
        self.primary_address = None
        self.city = None
        self.postal_code = None

    def print(self):
        data = []
        if self.postal_code:
            data.append(self.postal_code)
        if self.country:
            data.append(self.country)
        if self.city:
            data.append(self.city)
        if self.primary_address:
            data.append(self.primary_address)
        return ', '.join(data)