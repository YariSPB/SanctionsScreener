import requests
import config as c

def load_XML_UK():
    url = 'https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.xml'
    try:
        r = requests.get(url, allow_redirects=True)
        too = c.curr_dir + c.raw_data_dir + '/' + 'UK.xml'
        open(too, 'wb').write(r.content)
    except Exception as e:
        print('Failed to load xml from UK. Terminating.')
        print(str(e))
        exit()
