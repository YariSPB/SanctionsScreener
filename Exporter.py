from data_store import *
import config as c
import pathlib
import csv


class Exporter:
    def __init__(self, db: DataStore):
        pathlib.Path(c.curr_dir + c.export_dir).mkdir(exist_ok=True)
        self.data_store = db
