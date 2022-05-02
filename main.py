import ftplib
import pathlib
import os
import sqlite3
import xml.etree.ElementTree as ET

HOSTNAME = "ofacftp.treas.gov"
FOLDER_NAME = "/fac_delim"
USERNAME = "anonymous"
PASSWORD = "anonymous@domain.com"
curr_dir = os.getcwd()
raw_data_dir = '/raw_data'
raw_xml_name = '/sdn_advanced.xml'
db_dir = '/database'
SDN_DB_name = "SDN.db"

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def load_file(filename):
    # Connect FTP Server
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # force UTF-8 encoding
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(FOLDER_NAME)
    ftp_server.dir()

    # Enter File Name with Extension
    #filename = "sdn_advanced.xml"

    # Write file in binary mode
    with open(curr_dir + raw_data_dir +"/"+filename, "wb") as file:
        # Command for Downloading the file "RETR filename"
       ftp_server.retrbinary(f"RETR {filename}", file.write)

    # Close the Connection
    ftp_server.quit()


def create_SDN_DB():
    con = sqlite3.connect(curr_dir + db_dir+"/" + SDN_DB_name)
    cur = con.cursor()
    # Create table
    cur.execute('''CREATE TABLE IF NOT EXISTS DistinctParty
                   (FixedRef INTEGER PRIMARY KEY, 
                   PrimaryName TEXT,
                   EntityType INTEGER,
                   EntryDate TEXT,
                   BlockingSanctions INTEGER
                   )''')
    con.commit()
    con.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    #curr_dir = os.getcwd()
    #raw_data_dir = '/raw_data'
    pathlib.Path(curr_dir + raw_data_dir).mkdir(exist_ok=True)
    pathlib.Path(curr_dir + db_dir).mkdir(exist_ok=True)

    if not os.path.isfile(curr_dir + db_dir +"/" + SDN_DB_name):
        create_SDN_DB()

    if not os.path.isfile(curr_dir + raw_data_dir +raw_xml_name):
        print("No xml file: " +raw_xml_name)
        exit()

    tree = ET.parse(curr_dir + raw_data_dir +raw_xml_name)

    x=5



    #load_file('add.csv')
