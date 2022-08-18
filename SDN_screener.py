import ftplib
import os
import pathlib
from SDN_XML_reader import *
from SDN_exporter import SDN_exporter
import time
from os.path import exists


class SDN_screener:
    def __init__(self):
        self.file_data = []
        self.ftp_file_date={}
        pathlib.Path(c.curr_dir + c.raw_data_dir).mkdir(exist_ok=True)


    def load_new_SDN_and_export_CSV(self):
        if not self.new_SDN_issued():
            exit()

        load_SDN_file(c.raw_xml_name)
        xml_reader = SDN_XML_reader()
        all_SDN = xml_reader.get_all_SDN()
        csv_exporter = SDN_exporter()
        csv_exporter.export_to_file(all_SDN)


    def new_SDN_issued(self):
        if not exists(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name):
            return True

        try:
            print("Connecting to ftp ", c.HOSTNAME)
            # Connect FTP Server
            ftp_server = ftplib.FTP(c.HOSTNAME, c.USERNAME, c.PASSWORD)
        except Exception as e:
            print(str(e))
            exit()

        print("Connection established to ftp ", c.HOSTNAME)
        print("Loading SDN file from OFAC server... ")
        # force UTF-8 encoding
        ftp_server.encoding = "utf-8"
        ftp_server.cwd(c.FOLDER_NAME)
        # ftp_server.dir()
        self.file_data = []
        ftp_server.retrlines('LIST', self.__gather_file_date)
        ftp_server.quit()
        proposed_date = self.ftp_file_date[c.raw_xml_name]
        print('proposed_date:')
        print(proposed_date)

        if not proposed_date:
            print("Error of date screening " + c.FOLDER_NAME + c.raw_xml_name + " . Terminating")
            exit()

        xml_Reader = SDN_XML_reader()
        stored_max_date = xml_Reader.get_issue_date()
        print('Previously saved issue date:')
        print(stored_max_date)
        if stored_max_date >= proposed_date:
            print('No update required. Terminating')
            return False
        print('Update required. Continue.')
        return True

    def __gather_file_date(self, data_line):
        str_list = data_line.split()
        date = time.strptime(str_list[0], "%m-%d-%y")
        file_name = str_list[-1]
        self.ftp_file_date[file_name] = date
        self.file_data.append(data_line)


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

