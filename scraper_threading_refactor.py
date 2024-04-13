import os
import re
import requests
from bs4 import BeautifulSoup as Soup
from concurrent.futures import ThreadPoolExecutor

def determine_url_file_type(file_url):
    """
    Determine the file type based on the URL.
    """
    file_extension = file_url.split('.')[-1]
    if file_extension in ['pdf', 'zip', 'py']:
        return file_extension
    else:
        return None

def download_file(title, file_url, file_type, path):
    """
    Download the file from the given URL based on the specified file type.
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        # Define filename based on file type
        if file_type == 'pdf':
            filename = os.path.join(path, title + '.pdf')
        elif file_type == 'zip':
            filename = os.path.join(path, title + '.zip')
        elif file_type == 'py':
            filename = os.path.join(path, title + '.py')
        else:
            print(f"Unsupported file type: {file_type}")
            return

        # Write content to file
        with open(filename, 'wb') as f:
            f.write(response.content)

        # Check if file was successfully downloaded
        if os.path.isfile(filename):
            print(f"Download successful: {title}.{file_type}")
        else:
            print(f"Download failed: {title}.{file_type}")
    except requests.exceptions.RequestException as error:
        print(f"An error occurred while downloading {title}.{file_type}: {error}")
def download_files(parent_dir, url, directory):
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
                print('Download link not found for:', title)
                continue

            file_url = basis + href

            file_type = determine_url_file_type(file_url)
            if file_type:
                future = executor.submit(download_file, title, file_url, file_type, path)
                futures.append(future)
            else:
                print("Unsupported file type.")


        # Wait for all tasks to complete before proceeding.
        for future in futures:
            future.result()

# parent directory in which you intend to save the files
p_dir = 'e:\\supplementary\\6.0001 6.0002 Computation Python\\6.0002'
# the root site of the mitocw course
origin_url = "https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016"
# sections to download
url_lists = ["/pages/assignments/", "/pages/lecture-slides-and-files/"]
# url_lists = ["/pages/recitations/", "/pages/lecture-slides-code/"]
# /study-materials/ "/pages/exams/","/pages/study-materials/",
for item in url_lists:
    url = origin_url + item
    # should notice that the joint of two string should net contain two backslashes in a row
    print(url)
    dir = item.split("/")[2]
    print(dir)
    download_files(p_dir, url, dir)
