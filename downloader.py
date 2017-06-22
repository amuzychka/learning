# -- coding: utf-8 --
import requests
import os
import re
import io
from bs4 import BeautifulSoup

URL =  "http://lib.ru/lat/INOFANT/BRADBURY/"
PATTERN = "[^\s\-]{2,}"
ENCODING = 'utf-8'

def main():

    links = get_all_links()
    download_files(links)


def get_all_links():

    """
        Parsing main page (http://lib.ru/lat/INOFANT/BRADBURY/) to get names of all books

        :return: list of books that should be downloaded
    """
    links = []

    request = requests.get(URL).content                                                        # Getting main page 
    soup = BeautifulSoup(request, 'html.parser')                                               # Parsing html

    for link in soup.li.find_all('a'):                                                         # Getting second part of the link for each book from html list                                                         
        link_text = str(link.get('href'))
        if link_text.find("txt") != -1 and link_text.find("txt_Contents") == -1:               # Checking valid link text, pattern should be: some_text.txt
            links.append(link_text)

    return links                                                                               


def download_files(links):

    """
        Getting content for each book from the list and calling save_file method
        Example of links parameter: ['pillfire.txt', 'beda.txt']

        :param: links
    """

    for l in links:
        request = requests.get(URL + str(l)).content                                          # Getting book text, example of the link "http://lib.ru/lat/INOFANT/BRADBURY/pillfire.txt"
        save_file(request)


def save_file(request):

    """
        Parsing html of book content page, counting number of words and saving book text to the file

        :param: request
    """

    soup = BeautifulSoup(request, 'html.parser')                                              # Parsing html
    soup.encode('utf-8')                                                                      # Encoding to utf-8
    main_part = soup.pre                                                                      # Getting main part of html page

    if main_part.pre is None:                                                                 # Html can be separated into two parts, in this case we deleting first part with advertisements and using second
        soup.html.decompose()
        main_part = soup

    main_part.pre.pre.clear()                                                                 # Removing footer with scripts from html page
    text = main_part.pre.get_text()                                                           # Getting book text
    words_number = len(re.findall(PATTERN, text))                                             # Counting the number of words using pattern: "[^\s\-]{2,}" (all words that are longer than 2 characters)
    file_name = re.sub(r'[^\w\s]', '', main_part.pre.ul.h2.get_text())                        # Removing all invalid symbols from book name

    with io.open(file_name + '.txt', 'w', encoding=ENCODING) as f:                            # Saving book to the folder with script using story name as filename with extension .txt
        for a in text:
            f.write(a)

    print "File was saved: ", file_name, " Words number: ", words_number                      # Printing file name and number of words to console


if __name__ == "__main__":
    main()
