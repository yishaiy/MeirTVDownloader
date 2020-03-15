import os
import sys
import json
import requests
from bs4 import BeautifulSoup

import logging
logging.getLogger().level = logging.INFO



def main(config_path):
    config = json.load(open(config_path, 'rb'))

    if config['local_webpage']:
        logging.info('Getting page locally: {}'.format(config['local_webpage']))
        with open(config['local_webpage'], 'rb') as f:
            page = f.read()
    elif config['remote_webpage']:
        logging.info('Getting page from URL: {}'.format(config['remote_webpage']))
        page = requests.get(config['remote_webpage']).content

        webpage_localname = config['name'] + '.html'
        with open(webpage_localname, 'wb') as f:
            f.write(page)
        logging.info('Webpage saved to "{}"'.format(webpage_localname))
    else:
        logging.error('No webpage source..')
        return
    logging.debug('Page: {}'.format(page))

    soup = BeautifulSoup(page)

    lesson_divs = soup.find_all('div', {'class': 'tableset'})
    print lesson_divs[0]
    assert len(lesson_divs) == config['length']

    for div in lesson_divs:
        a = div.find('a', {'class': 'titleArchive'})
        lidx = re.find(".*idx=(.*).*", a)
        # logging.debug('{} {}'.format(lidx, div.attrs['data-sort']))
        assert lidx == div.attrs['data-sort']

        lnum = div.find_all('span', {'class': 'f-title'})[1].find('b').contents[0]
        assert int(lnum) >= 1 and int(lnum) <= config['length']
        
        lname = div.find('a', {'class': 'titleArchive'}).contents
        lname = lname[0] if lname != [] else config['default_name']
        lname = lname.translate({ord(unicode(ch)): None for ch in '!?"\''})
        
        # logging.debug('{idx} => {num} => {name}'.format(idx=lidx, num=lnum, name=lname))

        old_fname = config['dest_folder'] + config['old_filename'].format(idx=lidx)
        new_fname = config['dest_folder'] + config['new_filename'].format(num=lnum.rjust(len(str(config['length'])), '0'), name=lname)
        logging.info('Rename: "{old}" => "{new}"'.format(old=old_fname, new=new_fname))
        os.rename(old_fname, new_fname)









if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: python {} <config_path>'.format(sys.argv[0])
    else:
        main(sys.argv[1])
        print 'Done!'