import requests
from bs4 import BeautifulSoup as bs
import hashlib
from database.dbExecutor import dbExecutor
import datetime

SOURCE = 'MARIBOR-24'
base_url = 'https://maribor24.si'
full_urls = ['https://maribor24.si/lokalno/stran/',
             'https://maribor24.si/slovenija/stran/',
             'https://maribor24.si/gospodarstvo/stran/']
             #dodaj se stevilo strani - prva stran je 1
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}


def make_hash(title, date):
    return hashlib.sha1((title + date).encode('utf-8')).hexdigest()


def is_article_new(hash_str):
    if dbExecutor.getByHash(hash_str):
        return False
    print('new article found')
    return True


def get_title(soup):
    title = soup.find('h2')
    if title:
        return title.text.strip()
    print('title not found, update select() method')
    return 'title not found'


def get_date(soup):
    raw_date = soup.find('div', class_='post-details').find('span', class_='date')
    if raw_date:
        return raw_date.text.strip()
    print('Date not found, update select() method')
    return '1.1.1111'


def get_link(soup):
    link = soup.find('a')
    if link:
        return link.get('href')
    print('link not found')
    return base_url #return base url to avoid exceptions


def get_content(soup):
    content = soup.find('div', class_='post-content')
    if content:
        for script in content.find_all('script'):
            script.decompose()
        if content.find('div', class_='tagged-posts'): 
            content.find('div', class_='tagged-posts').decompose()
        return content.text.strip()
    print('content not found')
    return 'content not found'


def get_articles_on_pages(num_pages_to_check, session):
    articles = []
    for n in range(num_pages_to_check):
        for url in full_urls:
            r = session.get(url + str(n+1), timeout=10)
            soup = bs(r.text, 'html.parser')
            articles += soup.find_all('article', class_=True)
    return articles


def format_date(date):
    #format date for consistent database
    date = date.split('.')
    for i in range(2):
        if len(date[i]) == 1:
            date[i] = '0'+date[i]
    return '-'.join(reversed(date))


def main():
    num_pages_to_check = 1
    num_new_articles = 0
    articles_checked = 0

    with requests.Session() as session:
        session.headers.update(headers)

        articles = get_articles_on_pages(num_pages_to_check,session)
        articles_checked = len(articles)

        new_articles_tuples = []
        for x in articles:
            title = get_title(x)
            hash_str = make_hash(title, base_url) #datuma ni na prvi strani, namesto tega hash naredim iz base_url

            if is_article_new(hash_str):
                link = get_link(x)
                r = session.get(link, timeout=8)
                soup = bs(r.text, 'html.parser')
                date = get_date(soup)
                content = get_content(soup)
                print(link + '\n')
                new_tup = (str(datetime.date.today()), title, content, format_date(date), hash_str, link, SOURCE)
                new_articles_tuples.append(new_tup)
                num_new_articles += 1

        #add new articles to database
        dbExecutor.insertMany(new_articles_tuples)
        print(num_new_articles, 'new articles found,', articles_checked,'articles checked')


if __name__ == '__main__':
    main()