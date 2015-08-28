from selenium import webdriver
import json

import config

def setup():
    global s
    s = webdriver.Firefox()

def log(s):
    #print(s)
    pass

def login():
    s.get('https://www.bibliotheek.nl/ebooks')
    s.find_element_by_link_text('Inloggen').click()
    s.find_element_by_id("username").send_keys(config.username)
    s.find_element_by_id("password").send_keys(config.password)
    form = s.find_element_by_id('passwordForm')
    form.find_element_by_class_name('button').click()

def books_url():
    return 'https://www.bibliotheek.nl/ebooks/MijnBoekenplank'

def book_url(book_id):
    return ('https://cb.libreprint.com/Home/GetContentsComplex?' +
            'bookID=' + book_id)

def chapter_url(book_id, chapter_id):
    return ('https://cb.libreprint.com/Home/GetComponentComplex?' +
            'bookID=' + book_id + '&componentId=' + chapter_id +
            '&excludeCss=false')

def get_book(author, book_title, book_id):
    url = book_url(book_id)
    log(url); s.get(url)

    print author, book_title

    def chapter_key(chapter):
        chapter_id, chapter_title = chapter
        # chapter_id: "x9789023472193.html6.xhtml#toc_marker_9789023472193_-3"
        # Take the number at the end.
        return int(chapter_id.split('-')[-1])

    text = s.find_element_by_tag_name('body').text
    chapters = json.loads(text).items()
    for i, (chapter_id, chapter_title) in enumerate(
            sorted(chapters, key=chapter_key)):
        # chapter_id: "x9789023472193.html6.xhtml#toc_marker_9789023472193_-3"
        # Drop the part after the '#'.
        chapter_id = chapter_id.split('#')[0]

        url = chapter_url(book_id, chapter_id)
        log(url); s.get(url)

        #s.page_source
        print i, chapter_title
        break

def get_books():
    url = books_url()
    log(url); s.get(url)

    books = []
    for book in s.find_elements_by_class_name('content'):
        author = book.find_element_by_class_name('author').text
        title = book.find_element_by_tag_name('h4').text

        link_text = 'E-book online lezen'
        links = book.find_elements_by_link_text(link_text)
        if not links:
            log('Skipping: ' + author + ' - ' + title)
            log('No link text "' + link_text + '"')
            continue

        book_id = links[0].get_attribute('href').split('?id=')[1]
        books.append((author, title, book_id))

    for author, title, book_id in books:
        get_book(author, title, book_id)

# Willem Frederik Hermans
# De laatste roker
sample_book_id = '43476e47-ee8f-4f53-986a-778a80d87f52'

def main():
    setup()
    login()
    get_book(sample_book_id)

if __name__ == '__main__':
    main()
