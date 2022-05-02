import ftplib

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    HOSTNAME = "ofacftp.treas.gov"
    COMMAND_NAME = "/fac_delim"
    USERNAME = "anonymous"
    PASSWORD = "anonymous@domain.com"

    # Connect FTP Server
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # force UTF-8 encoding
    ftp_server.encoding = "utf-8"

    ftp_server.dir()

    # Close the Connection
    ftp_server.quit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
