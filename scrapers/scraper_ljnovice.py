from bs4 import BeautifulSoup
import requests
import hashlib
''' 
    scraper je uporaben za vec projektov
'''

base_url = 'https://ljnovice.si'
full_url = 'https://ljnovice.si/page/' #kasneje dodas se stevilko strani (1, 2, ..)
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}


def makeHash(title, date):
    return hashlib.sha1((title+date).encode('utf-8')).hexdigest()


def isArticleNew(hash):
    is_new = False
    try:
        f = open(('article_list.txt'), 'r+')
    except FileNotFoundError:
        f = open(('article_list.txt'), 'a+')

    if hash not in f.read().split():
        is_new = True
        f.write(hash + '\n')
        print('new article found')
    f.close()
    return is_new


def getLink(soup):
    link = soup.select('article > header > h2 > a')
    if link:
        return link[0].get('href')
    print('link not found, update select() method')
    return 'link not found'


def getDate(soup):
    raw_date = soup.find('time')
    if raw_date:
        return raw_date.text
    print('Date not found, update select() method')
    return 'date not found'


def getTitle(soup):
    title = soup.select('article > header > h2 > a')
    if title:
        return ' '.join(title[0].text.split())
    print('title not found, update select() method')
    return 'title not found'


def getContent(url, session):
    r = session.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    content =  soup.find('div', class_='entry-content clearfix')
    if content:
        return ' '.join(content.text.split())
    print('content not found, update select() method')
    return 'content not found'


def getArticlesOn_n_pages(num_pages_to_check, session):
    articles = []
    for n in range(num_pages_to_check):
        r = session.get(full_url + str(n+1), timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        articles_on_page = soup.find_all('div', class_='post-column clearfix')
        articles = articles + articles_on_page
    return articles


def main():
    num_pages_to_check = 4
    num_new_articles = 0

    with requests.Session() as session:
        session.headers.update(headers)
        articles = getArticlesOn_n_pages(num_pages_to_check, session)
        articles_checked = len(articles)

        dates = []
        titles = []
        hashes = []
        links = []

        for x in articles:
            title = getTitle(x)
            date = getDate(x)
            hash = makeHash(title, date)

            if isArticleNew(hash):
                titles.append(title)
                dates.append(date)
                hashes.append(hash)
                links.append(getLink(x))
                num_new_articles += 1

        for i in range(len(links)):
            content = getContent(links[i], session)
            print(titles[i])
            print(dates[i])
            print(" ".join(content.split()), '\n\n')

    print(num_new_articles, 'new articles found,', num_pages_to_check,'pages checked -', articles_checked, 'articles checked')

if __name__ == '__main__':
    main()