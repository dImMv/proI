from bs4 import BeautifulSoup
import dbrepo
import parse
import stats
import sqlite3
import requests
import os.path

conn = get_connection()
src = get_src()
soup = BeautifulSoup(src.text, "html.parser")
fill_db(conn, soup)
print_stats(conn)
conn.close()

def get_connection():
    conn = None
    while conn is None:
        db_filename = input('Enter the database filename: ') + '.db'
        conn = dbrepo.create_connection(db_filename)
    return conn

def create_connection(db_filename: str):
    conn = None
    if os.path.isfile(db_filename):
        print(f'Database with name \'{db_filename}\' already exists.')
        print('Enter another name.\n')
    else:
        conn = sqlite3.connect(db_filename)
        cur = conn.cursor()
        command_tags = '''
        CREATE TABLE "tags" (
        	"id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "tag"	TEXT,
	        "count"	INTEGER,
	        "frequency"	REAL
	    );'''
        command_words = '''
        CREATE TABLE "words" (
        	"id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "word"	TEXT,
	        "count"	INTEGER,
	        "frequency"	REAL
        );'''
        command_links = '''
        CREATE TABLE "links" (
	        "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "link"	TEXT
        );'''
        command_images = '''
        CREATE TABLE "images" (
	        "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "image"	TEXT
        );'''
        cur.execute(command_tags)
        cur.execute(command_words)
        cur.execute(command_links)
        cur.execute(command_images)
        conn.commit()
    return conn

def get_src():
    src = None
    while src is None:
        try:
            url = input('Enter the name of URL adress: ')
            src = requests.get(url)
        except requests.exceptions.RequestException:
            print('E: incorrect URL')
            print('Enter URL again\n')
    return src
def process_tags(conn: sqlite3.Connection, soup: BeautifulSoup):
    tags = parse.get_tags(soup)
    unique_tags = list(dict.fromkeys(tags))
    for item_id in range(0, len(unique_tags)):
        tag = unique_tags[item_id]
        count = tags.count(tag)
        frequency = count / len(tags)
        fields = (item_id, tag, count, frequency)
        dbrepo.insert_tag(conn, fields)


def process_links(conn: sqlite3.Connection, soup: BeautifulSoup):
    links = parse.get_links(soup)
    for item_id in range(0, len(links)):
        link = links[item_id]
        fields = (item_id, link)
        dbrepo.insert_link(conn, fields)


def process_images(conn: sqlite3.Connection, soup: BeautifulSoup):
    images = parse.get_images(soup)
    for item_id in range(0, len(images)):
        image = images[item_id]
        fields = (item_id, image)
        dbrepo.insert_image(conn, fields)

def fill_db(conn: sqlite3.Connection, soup: BeautifulSoup):
    process_words(conn, soup)
    process_tags(conn, soup)
    process_links(conn, soup)
    process_images(conn, soup)

def insert_tag(conn: sqlite3.Connection, fields: tuple):
    cur = conn.cursor()
    cur.execute("INSERT INTO tags VALUES (?, ?, ?, ?)", fields)
    conn.commit()


def insert_word(conn: sqlite3.Connection, fields: tuple):
    cur = conn.cursor()
    cur.execute("INSERT INTO words VALUES (?, ?, ?, ?)", fields)
    conn.commit()


def insert_link(conn: sqlite3.Connection, fields: tuple):
    cur = conn.cursor()
    cur.execute("INSERT INTO links VALUES (?, ?)", fields)
    conn.commit()


def insert_image(conn: sqlite3.Connection, fields: tuple):
    cur = conn.cursor()
    cur.execute("INSERT INTO images VALUES (?, ?)", fields)
    conn.commit()


def process_words(conn: sqlite3.Connection, soup: BeautifulSoup):
    words = parse.get_words(soup.text)
    unique_words = list(dict.fromkeys(words))
    for item_id in range(0, len(unique_words)):
        word = unique_words[item_id]
        count = words.count(word)
        frequency = count / len(words)
        fields = (item_id, word, count, frequency)
        dbrepo.insert_word(conn, fields)

def print_stats(conn: sqlite3.Connection):
    words = stats.get_most_used_words(conn)
    tags = stats.get_most_used_tags(conn)
    print(f'{len(words)} most used words:')
    for i in range(0, len(words)):
        print(f'\t{i + 1}. {words[i]}')
    print()
    print(f'{len(tags)} most used HTML-tags:')
    for i in range(0, len(tags)):
        print(f'\t{i + 1}. <{tags[i]}>')
    print()
    print(f'Links on page: {stats.get_count_links(conn)}')
    print(f'Images on page: {stats.get_count_images(conn)}')

def get_words(page_text: str):
    text = page_text.replace('\n', ' ').replace('\r', ' ')
    for char in text:
        if not char.isalpha():
            text = text.replace(char, ' ')
    words = text.split(' ')
    while '' in words:
        words.remove('')
    return words


def get_tags(soup: BeautifulSoup):
    tags = []
    for child in soup.recursiveChildGenerator():
        if child.name:
            tags.append(child.name)
    return tags


def get_links(soup: BeautifulSoup):
    links = []
    all_a = soup.find_all("a")
    for item in all_a:
        link = item.get("href")
        if link is None or link == '':
            continue
        else:
            links.append(link)
    return links


def get_images(soup: BeautifulSoup):
    images = []
    all_img = soup.find_all("img")
    for item in all_img:
        image = item.get("src")
        if image is None or image == '':
            continue
        else:
            images.append(image)
    return images

def get_count_links(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM links')
    count = cur.fetchall()[0][0]
    return count


def get_count_images(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM images')
    count = cur.fetchall()[0][0]
    return count


def get_most_used_words(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute('SELECT * FROM words ORDER BY count DESC LIMIT 10')
    words = []
    query_result = cur.fetchall()
    for i in range(0, len(query_result)):
        words.append(query_result[i][1])
    return words


def get_most_used_tags(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute('SELECT * FROM tags ORDER BY count DESC LIMIT 10')
    tags = []
    query_result = cur.fetchall()
    for i in range(0, len(query_result)):
        tags.append(query_result[i][1])
    return tags