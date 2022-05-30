import xml.etree.ElementTree as ET
import config as c
from entities import *

tax_id_ref = '1596'
p = c.tree_prefix


class SDN_XML_Store:
    def __init__(self):
        self.tree = ET.parse(c.curr_dir + c.raw_data_dir + '/' + c.raw_xml_name)

