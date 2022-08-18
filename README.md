# SanctionsScreener
With ever increasing amount of new sanctioned entities, it has become more time consuming to track them. As such, compliance officers maintain Excel spreadsheets by manually adding new sanctioned entries and verifying them against lists of clients. This project aims to reduce manual labour by automatically parsing sanctions from official government websites and presenting them in a desirable format.
Currently, it fetches all SDN entities from OFAC (Office of Foreign Assets Control, USA) and complements them with relevant properties.

Launch: simply running main.py will generane SDN.csv file.

Technology: first, the program fetches new SDN file using ftp channel. Second, it parses XML SDN file for useful facts. Lastly, it exports SDN into CSV file.

Architecture:
- main.py is a launcher.
- SDN_screener.py does loading from OFAC's ftp server and calls XML parser and CSV exporter.
- SDN_XML_reader.py is responsible for parsing complex interlinked data from the XML file into desirable format. To begin with, it eagerly iterates over entire XML file and collects relevant data into Python dictionaries in O(n) time. Furthermore, it links principal SDN entities with discovered properties.
- SDN_exporter.py flattens collected SDN data into spreadsheet rows and saves a .csv. Its another responsibility is filtering out illegal characters. 




