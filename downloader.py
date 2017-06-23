# -- coding: utf-8 --
import requests
import argparse
import os
import re
import io
from bs4 import BeautifulSoup

PATTERN = "[^\s\-]{2,}"
ENCODING = 'utf-8'

def main(args):

    links = get_all_links(args.url)
    download_files(links, args)


def get_all_links(url):

    """
        Parsing main page (http://lib.ru/lat/INOFANT/BRADBURY/) to get names of all books

        :return: list of books that should be downloaded
    """
    try:
        # Getting main page 
        request = requests.get(url).content
    except Exception:
        print "Error: Bad response!"

    # Parsing html
    soup = BeautifulSoup(request, 'html.parser')

    # Getting second part of the link for each book from html list
    for link in soup.li.find_all('a'):                                                       
        link_text = str(link.get('href'))

        # Checking valid link text, pattern should be: some_text.txt
        if link_text.find("txt") != -1 and link_text.find("txt_Contents") == -1:
            yield link_text                                                                              


def download_files(links, args):

    """
        Getting content for each book from the list and calling save_file method
        Example of links parameter: ['pillfire.txt', 'beda.txt']

        :param: links
    """

    for l in links:
        try:
            # Getting book text, example of the link "http://lib.ru/lat/INOFANT/BRADBURY/pillfire.txt"
            url = os.path.join(args.url, l)
            request = requests.get(url).content
        except Exception:
            print "Error: Bad response!"

        save_file(request, args)


def save_file(request, args):

    """
        Parsing html of book content page, counting number of words and saving book text to the file

        :param: request
    """
    # Parsing html
    soup = BeautifulSoup(request, 'html.parser')
    # Encoding to utf-8
    soup.encode('utf-8')
    # Getting main part of html page
    main_part = soup.pre

    # Html can be separated into two parts, 
    # in this case we deleting first part with advertisements and using second
    if main_part.pre is None:
        soup.html.decompose()
        main_part = soup

    # Removing footer with scripts from html page
    main_part.pre.pre.clear()
    # Getting book text
    text = main_part.pre.get_text()
    # Counting the number of words using pattern: "[^\s\-]{2,}" (all words that are longer than 2 characters)
    words_number = len(re.findall(PATTERN, text))
    # Removing all invalid symbols from book name
    file_name = re.sub(r'[^\w\s]', '', main_part.pre.ul.h2.get_text())
    
    folder_path = os.path.abspath(args.folder)

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    file_path = os.path.join(folder_path, file_name + ".txt")

    if os.path.isfile(file_path) and not str2bool(args.force):
        print "Book ", file_name, " already downloaded"
    else:
        # Saving book to the folder with script using story name as filename with extension .txt
        # Using io library because it has possibility to specify ENCODING (it will crash without this)
        with io.open(file_path, 'w', encoding=ENCODING) as f:
            f.write(text)
        print "File was saved: ", file_name, " Words number: ", words_number


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help="URL that you want to parse", type=str, default="http://lib.ru/lat/INOFANT/BRADBURY/")
    parser.add_argument('--folder', help="Folder to save the results", type=str, default=os.getcwd())
    parser.add_argument('--force', help="Do we need to rewrite file if exist?", type=str, default="false")

    args = parser.parse_args()

    main(args)
