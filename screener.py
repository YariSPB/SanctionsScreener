import ftplib
from data_store import *
import config as c
import pathlib


class Screener:
    def __init__(self, db: DataStore):
        self.data_store = db
        self.file_data = []
        pathlib.Path(c.curr_dir + c.raw_data_dir).mkdir(exist_ok=True)


    def load_if_new_SDN_published(self):
        if not self.new_SDN_published():
            return
        self.load_SDN_file(c.raw_xml_name)

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

        for entry in self.file_data:
            entry_segments = entry.split()
            if entry_segments[-1] == c.raw_xml_name:
                print(entry)
                proposed_date = entry_segments[0]
                break

        if not proposed_date:
            print("Error screening " + c.FOLDER_NAME + c.raw_xml_name + " . Terminating")
            exit()

        stored_max_date = self.data_store.get_latest_entry_date()
        if not stored_max_date:
            return True

        if stored_max_date >= proposed_date:
            return False
        return True

    def __gather_file_data(self, data_line):
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
        ftp_server.dir()

        # Write file in binary mode
        with open(c.curr_dir + c.raw_data_dir + "/" + filename, "wb") as file:
            # Command for Downloading the file "RETR filename"
            ftp_server.retrbinary(f"RETR {filename}", file.write)
        # Close the Connection
        ftp_server.quit()

        if not os.path.isfile(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name):
            print("XML download failed. No xml file exists : " + '/' + c.raw_xml_name)
            exit()



