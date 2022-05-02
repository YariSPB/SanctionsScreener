import ftplib
import pathlib
import os
import sqlite3

HOSTNAME = "ofacftp.treas.gov"
FOLDER_NAME = "/fac_delim"
USERNAME = "anonymous"
PASSWORD = "anonymous@domain.com"
curr_dir = os.getcwd()
raw_data_dir = '/raw_data'
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
    conn = sqlite3.connect(curr_dir + db_dir+"/" + SDN_DB_name)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    #curr_dir = os.getcwd()
    #raw_data_dir = '/raw_data'
    pathlib.Path(curr_dir + raw_data_dir).mkdir(exist_ok=True)
    pathlib.Path(curr_dir + db_dir).mkdir(exist_ok=True)

    if not os.path.isfile(curr_dir + db_dir +"/" + SDN_DB_name):
        create_SDN_DB()


    #load_file('add.csv')
