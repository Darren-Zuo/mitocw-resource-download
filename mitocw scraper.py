import os
import re
import requests
from bs4 import BeautifulSoup as Soup


def download_pdfs(parent_dir, url, directory):
    ii = 0
    basis = 'https://ocw.mit.edu'

    # create the downloading path name
    path = os.path.join(parent_dir, directory)
    if not os.path.exists(path):
        os.mkdir(path)

    # go to the site where href links are included
    # url = "https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008//pages/assignments/"
    r = requests.get(url=url)
    text = r.content.decode('utf-8')
    soup = Soup(text, 'html.parser')

    # find the section containing those links
    content = soup.find('main', {'id': 'course-content-section'})

    for link in content.find_all('a'):
        ii = ii + 1
        # td_text = link.parent.text.strip()
        #
        # title = re.sub(r'\s*\(.*?\)\s*', '', td_text)
        td_text = link.text
        title = re.sub(r'\s*\(.*?\)\s*', '', td_text) # removing "(PDF)" from title
        title = str(ii) + " " + title
        # define forbidden characters in naming a file
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

        # ruling out these characters from the title
        for char in forbidden_chars:
            title = title.replace(char, '')

        print(title)

        # get the pdf site
        href = link.get('href')

        # sometimes it points to a paper or some other files
        if not href.startswith('/courses'):
            print('this url points to an anomalous file')
            print(href)
            continue

        href = basis + href
        print(href)
        # print(href)
        r1 = requests.get(url=href)
        text1 = r1.content.decode('utf-8')
        soup1 = Soup(text1, 'html.parser')

        # title = soup1.find('h2', {'class','pb-1 mb-1'}).text
        # # define forbidden characters in naming a file
        # forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        #
        # # ruling out these characters from the title
        # for char in forbidden_chars:
        #     title = title.replace(char, '')
        #
        # print(title)


        # In case the hyperlink fetched is not a pdf file, raise an exception and continue running.
        try:
            href = soup1.find('a', {'class', 'download-file'}).get('href')
        except AttributeError:
            print('PDF link not found for:', title)
            continue

        # jumps to a site ends with .pdf (pdf浏览网页)
        pdf_url = basis + href

        # this piece of code is only able to download pdf files, other kinds of sites will be displayed in the output
        if not pdf_url.endswith('.pdf'):
            print('this url points to an anomalous file')
            print(pdf_url)
            continue

        try:
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            print(f"HTTP error occurred: {http_error}")
        except requests.exceptions.ConnectionError as connection_error:
            print(f"Connection error occurred: {connection_error}")
        except requests.exceptions.Timeout as timeout_error:
            print(f"Timeout error occurred: {timeout_error}")
        except requests.exceptions.RequestException as request_error:
            print(f"An error occurred: {request_error}")

        filename = os.path.join(path, title + '.pdf') #
        print(filename)
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)

        if os.path.isfile(filename):
            print("Download successful.")
        else:
            print("Download failed.")


# parent directory in which you intend to save the files
p_dir = 'E:\\supplementary\\通信课程\\6.041 Probabilistic Systems Analysis And Applied Probability'
# the root site of the mitocw course
origin_url = "https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010"
# sections to download
url_lists = ["/pages/lecture-notes/"]
# url_lists = ["/pages/recitations/", "/pages/tutorials/"]
# /study-materials/ "/pages/exams/","/pages/study-materials/",
for item in url_lists:
    url = origin_url + item
    # should notice that the joint of two string should net contain two backslashes in a row
    print(url)
    dir = item.split("/")[2]
    print(dir)
    download_pdfs(p_dir, url, dir)
