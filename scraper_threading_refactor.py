import os
import re
import requests
from bs4 import BeautifulSoup as Soup
from concurrent.futures import ThreadPoolExecutor

def download_pdf(title, pdf_url, path):
    try:
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        filename = os.path.join(path, title + '.pdf')
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)

        if os.path.isfile(filename):
            print(f"Download successful: {title}.pdf")
        else:
            print(f"Download failed: {title}.pdf")
    except requests.exceptions.RequestException as error:
        print(f"An error occurred while downloading {title}.pdf: {error}")

def download_pdfs(parent_dir, url, directory):
    basis = 'https://ocw.mit.edu'
    path = os.path.join(parent_dir, directory)

    if not os.path.exists(path):
        os.mkdir(path)

    r = requests.get(url=url)
    text = r.content.decode('utf-8')
    soup = Soup(text, 'html.parser')
    content = soup.find('main', {'id': 'course-content-section'})

    with ThreadPoolExecutor(max_workers=5) as executor:
        ii = 0
        futures = []

        for link in content.find_all('a'):
            ii += 1
            td_text = link.text
            title = re.sub(r'\s*\(.*?\)\s*', '', td_text)  # removing "(PDF)" from title
            title = str(ii) + " " + title
            forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

            for char in forbidden_chars:
                title = title.replace(char, '')

            href = link.get('href')

            if not href.startswith('/courses'):
                print('this url points to an anomalous file')
                print(href)
                continue

            href = basis + href
            r1 = requests.get(url=href)
            text1 = r1.content.decode('utf-8')
            soup1 = Soup(text1, 'html.parser')

            try:
                href = soup1.find('a', {'class', 'download-file'}).get('href')
            except AttributeError:
                print('PDF link not found for:', title)
                continue

            pdf_url = basis + href

            if not pdf_url.endswith('.pdf'):
                print('this url points to an anomalous file')
                print(pdf_url)
                continue

            future = executor.submit(download_pdf, title, pdf_url, path)
            futures.append(future)

        # Wait for all tasks to complete before proceeding.
        for future in futures:
            future.result()

# parent directory in which you intend to save the files
p_dir = 'E:\\supplementary\\14.01SC microeconomics'
# the root site of the mitocw course
origin_url = "https://ocw.mit.edu/courses/14-01-principles-of-microeconomics-fall-2018"
# sections to download
url_lists = ["/pages/lecture-notes/", "/pages/problem-sets/", "/pages/exams/"]
# url_lists = ["/pages/recitations/", "/pages/tutorials/"]
# /study-materials/ "/pages/exams/","/pages/study-materials/",
for item in url_lists:
    url = origin_url + item
    # should notice that the joint of two string should net contain two backslashes in a row
    print(url)
    dir = item.split("/")[2]
    print(dir)
    download_pdfs(p_dir, url, dir)
