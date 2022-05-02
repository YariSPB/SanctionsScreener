import ftplib
import pathlib
import os

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    HOSTNAME = "ofacftp.treas.gov"
    FOLDER_NAME = "/fac_delim"
    USERNAME = "anonymous"
    PASSWORD = "anonymous@domain.com"
    curr_dir = os.getcwd()
    raw_data_dir = '/raw_data'

    pathlib.Path(curr_dir + raw_data_dir).mkdir(exist_ok=True)

    # Connect FTP Server
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # force UTF-8 encoding
    ftp_server.encoding = "utf-8"



    ftp_server.cwd(FOLDER_NAME)

    ftp_server.dir()

    # Enter File Name with Extension
    filename = "sdn_advanced.xml"

    # Write file in binary mode
    with open(curr_dir + raw_data_dir +"/"+filename, "wb") as file:
        # Command for Downloading the file "RETR filename"
       ftp_server.retrbinary(f"RETR {filename}", file.write)


    # Close the Connection
    ftp_server.quit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
