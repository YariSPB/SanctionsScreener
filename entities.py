class Person:
    def __init__(self):
        self.primary_name = None
        self.gender = None
        self.secondary_latin = []
        self.secondary_cyrillic = []
        self.birth_date = None
        self.nationality = None
        self.tax_id = None


class SDN_Person(Person):
    def __init__(self, parent, fix_id, date, programs):
        self.person = parent
        self.sdn_id = fix_id
        self.date = date
        self.programs = programs
