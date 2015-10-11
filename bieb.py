import os
import shutil
import time

from selenium import webdriver

import config

def setup():
    global s
    s = webdriver.Firefox()

def log(s):
    print(s)
    pass

def get(url):
    log('--> ' + url)
    s.get(url)
    time.sleep(0.5)

def login():
    get('https://www.bibliotheek.nl/ebooks')
    s.find_element_by_link_text('Inloggen').click()
    s.find_element_by_id("username").send_keys(config.username)
    s.find_element_by_id("password").send_keys(config.password)
    form = s.find_element_by_id('passwordForm')
    form.find_element_by_class_name('button').click()
    time.sleep(0.5)

def chapter_url(book_id, chapter_id):
    return ('https://cb.libreprint.com/Home/GetComponentComplex?' +
            'bookID=' + book_id + '&componentId=' + chapter_id +
            '&excludeCss=false')

def get_chapters(book_dir, book_url):
    get(book_url)
    book_id = book_url.split('?id=')[1]

    shutil.rmtree(book_dir, True)
    os.makedirs(book_dir)
    log('Creating ' + book_dir)

    chapter_ids = s.execute_script('return getComponentsPassTrough()();')
    chapter_ids = [c for c in chapter_ids if c != 'voorblad.html']

    for i, chapter_id in enumerate(chapter_ids):
        get(chapter_url(book_id, chapter_id))

        filename = str(i).rjust(2, '0') + '.html'
        filepath = os.path.join(book_dir, filename)
        with open(filepath, 'w') as f:
            f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8">')

            f.write('''
<style type="text/css">
    span.wpt-cursief { font-style: italic; }
    span.wpt-vet { font-weight: bold; }
    span.wpt-vetcursief { font-style: italic; font-weight: bold }
    span.wpt-romein { font-style: italic; }
</style>
            ''')

            f.write(s.page_source.encode('UTF-8'))
            log('Writing ' + filepath)

def get_books():
    get('https://www.bibliotheek.nl/ebooks/MijnBoekenplank')

    # Store books in list first, to prevent "Element not found in the
    # cache".
    books = []
    for book in s.find_elements_by_class_name('content'):
        author = book.find_element_by_class_name('author').text
        title = book.find_element_by_tag_name('h4').text

        book_dir = 'boeken/{author}-{title}'.format(author=author, title=title)

        links = book.find_elements_by_link_text('E-book online lezen')
        if not links:
            log('Skipping "' + book_dir + '". No link text.')
            continue

        if os.path.exists(book_dir):
            log('Skipping "' + book_dir + '". Already exists.')
            continue

        book_url = links[0].get_attribute('href')
        books.append((book_dir, book_url))

    for book_dir, book_url in books:
        get_chapters(book_dir, book_url)

def main():
    setup()
    login()
    get_books()

if __name__ == '__main__':
    main()
