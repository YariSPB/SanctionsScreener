import ftplib
from data_store import *
import config as c
import pathlib
from XmlReader import *
from Exporter import Exporter
import time


class Screener:
    def __init__(self, db: DataStore):
        self.data_store = db
        self.csv_exporter = Exporter(db)
        self.file_data = []
        self.ftp_file_data={}
        pathlib.Path(c.curr_dir + c.raw_data_dir).mkdir(exist_ok=True)


    def get_new_SDN(self):
        if not self.new_SDN_published():
            print('No new SDN entries. Terminating')
            exit()
        self.load_SDN_file(c.raw_xml_name)
        xml_r = XmlReader()
        xml_r.load_all_SDN_persons()
        self.data_store.insert_sdn_persons(xml_r.SDN_Persons)
        self.csv_exporter.export_sdn_csv()


    def new_SDN_published(self):
        try:
            print("Connecting to ftp ", c.HOSTNAME)
            # Connect FTP Server
            ftp_server = ftplib.FTP(c.HOSTNAME, c.USERNAME, c.PASSWORD)
        except Exception as e:
            print(str(e))
            exit()

        print("Connection established to ftp ", c.HOSTNAME)

        # force UTF-8 encoding
        ftp_server.encoding = "utf-8"
        ftp_server.cwd(c.FOLDER_NAME)
        # ftp_server.dir()
        self.file_data = []
        ftp_server.retrlines('LIST', self.__gather_file_data)
        ftp_server.quit()

        print(self.file_data)

        proposed_date = self.ftp_file_data[c.raw_xml_name]

        if not proposed_date:
            print("Error screening " + c.FOLDER_NAME + c.raw_xml_name + " . Terminating")
            exit()

        stored_max_date = self.data_store.get_latest_sdnperson_date()
        if not stored_max_date:
            return True

        db_Date = time.strptime(stored_max_date, "%Y-%m-%d")
        if db_Date >= proposed_date:
            return False
        return True

    def __gather_file_data(self, data_line):
        str_list = data_line.split()
        date = time.strptime(str_list[0], "%m-%d-%y")
        file_name = str_list[-1]
        self.ftp_file_data[file_name] = date
        self.file_data.append(data_line)

    @staticmethod
    def load_SDN_file(filename):
        try:
            print("Connecting to ftp ", c.HOSTNAME)
            # Connect FTP Server
            ftp_server = ftplib.FTP(c.HOSTNAME, c.USERNAME, c.PASSWORD)
        except Exception as e:
            print(str(e))
            exit()

        print("Connection established to ftp ", c.HOSTNAME)

        # force UTF-8 encoding
        ftp_server.encoding = "utf-8"
        ftp_server.cwd(c.FOLDER_NAME)
        #ftp_server.dir()

        # Write file in binary mode
        with open(c.curr_dir + c.raw_data_dir + "/" + filename, "wb") as file:
            # Command for Downloading the file "RETR filename"
            ftp_server.retrbinary(f"RETR {filename}", file.write)
        # Close the Connection
        ftp_server.quit()

        if not os.path.isfile(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name):
            print("XML download failed. No xml file exists : " + '/' + c.raw_xml_name)
            exit()



