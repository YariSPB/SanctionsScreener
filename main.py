import pathlib
import os
from XmlReader import *
from screener import *
from Exporter import *
import sqlite3
import re

if __name__ == '__main__':
    print("SDN Screener started.")

    data_store = DataStore()
    screener = Screener(data_store)
    screener.load_new_SDN_and_export_CSV()
    exit()



