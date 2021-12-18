import os
import sys
import json
import requests
import traceback
from bs4 import BeautifulSoup

import logging
logging.getLogger().level = logging.INFO





# def download_mp3(url, filepath):
#     logging.debug("Downloading file URL '{url}' into '{filepath}'".format(url=url, filepath=filepath))
#     try:
#         resp = requests.get(url, stream=True)
        
#         with open(filepath, 'wb') as f:
#             for chunk in resp.iter_content(chunk_size=2048):
#                 if chunk: # filter out keep-alive new chunks
#                     f.write(chunk)
        
#         logging.debug("Download finished successfully!")
#     except Exception, e:
#         logging.error("Error downloading file URL '{url}' into '{filepath}'".format(url=url, filepath=filepath))
#         logging.error("Exception: {}".format(e.message))
#         # logging.error("Traceback: {}".format(traceback.format_exc()))


FILE_OBJ = None
INDEX = 1
INDEX_LEN = 3  # number of digits in the index of lesson


def rename(line):
    idx, url, filename, title, ref = line.split('||')
    # ref = ref.translate(None, '!?"')
    title = title.translate(None, '!?"\'')
    newfilename = '{idx}_{name}.mp3'.format(idx=idx, name=title).decode('utf8')
    print '{0} => {1}'.format(filename, repr(newfilename))
    if os.path.exists(filename):
        os.rename(filename, newfilename)


def info_lesson(url, prev_url=''):
    global FILE_OBJ, INDEX, INDEX_LEN

    try:
        # Index
        this_idx = str(INDEX).rjust(INDEX_LEN, '0')
        print 'Idx: {}'.format(this_idx)
        FILE_OBJ.write(this_idx + '||')

        # Url
        print 'Url: {}'.format(url)
        FILE_OBJ.write(url + '||')

        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")

        links = [a.attrs['href'] for a in soup.find_all('a', {'class': 'jet-listing-dynamic-link__link'})]

        # MP3 filename
        mp3_url = [link for link in links if link[-4:] == '.mp3']
        mp3_url = mp3_url[0] if len(mp3_url) > 0 else '/'
        mp3_file = mp3_url.split('/')[-1]
        print 'Mp3 file: "{}"'.format(mp3_file)
        FILE_OBJ.write(mp3_file + '||')

        # Title
        title_div = soup.find_all('div', {'class': 'elementor-page-title'})[0]
        h1_title = title_div.find_all('h1', {'class': 'elementor-heading-title'})[0]
        title = h1_title.text
        print 'Title: "{}"'.format(title.encode('utf8'))
        FILE_OBJ.write(title.encode('utf8') + '||')

        # Perek + Pasuk
        ref_div = soup.find_all('div', {'data-id': 'd3fd816'})[0]
        ref_div = ref_div.find_all('div', {'class': 'elementor-text-editor'})[0]
        ref_text = ref_div.text.strip()
        print 'Reference: "{}"'.format(ref_text.encode('utf8'))
        FILE_OBJ.write(ref_text.encode('utf8'))


        lessons_links = [link for link in links if link[-1] == '/']
        assert len(lessons_links) in [1, 2]
        next_url = filter(lambda link: link != prev_url, lessons_links)
        if next_url == []:
            next_url = None
        else:
            next_url = next_url[0]
        print 'Next url: {}'.format(next_url)

        return (next_url, url)
    finally:
        FILE_OBJ.write('\n')


def download_lesson(url, prev_url=''):
    print 'Url: {}'.format(url)
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    links = [a.attrs['href'] for a in soup.find_all('a', {'class': 'jet-listing-dynamic-link__link'})]

    print links

    mp3_url = [link for link in links if link[-4:] == '.mp3']
    if len(mp3_url) == 0:
        print 'No mp3 url for this lesson!'
        os.system('touch {}_no_mp3_file'.format(url.rstrip('/').split('/')[-1]))
    else:
        mp3_url = mp3_url[0]
        print 'Mp3 url: {}'.format(mp3_url)
        os.system('wget -q "{}"'.format(mp3_url))

    lessons_links = [link for link in links if link[-1] == '/']
    assert len(lessons_links) in [1, 2]

    next_url = filter(lambda link: link != prev_url, lessons_links)
    if next_url == []:
        next_url = None
    else:
        next_url = next_url[0]
    print 'Next url: {}'.format(next_url)
    return (next_url, url)


def main(next_url, prev_url='', index=''):
    global FILE_OBJ, INDEX
    FILE_OBJ = open('lessons_info.txt', 'ab')
    INDEX = index or 1

    # prev_url = ''

    # func = info_lesson
    func = download_lesson

    while next_url is not None:
        print '-'*40
        print 'Index: {}'.format(INDEX)
        print 'Next, Prev : {}'.format([next_url, prev_url])
        next_url, prev_url = func(next_url, prev_url=prev_url)
        INDEX += 1

    FILE_OBJ.close()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'NOTE: script for meirTV at 18.5.2021.. (site changed)'
        print 'Usage: python {} <lesson_url> [index]'.format(sys.argv[0])
    else:
        main(sys.argv[1], '' if len(sys.argv) < 3 else sys.argv[2])
        print 'Done!'