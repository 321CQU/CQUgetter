from typing import List, Dict

from bs4 import BeautifulSoup
from requests import Session


class BookSearchSet:
    search_url = "http://lib.cqu.edu.cn/asset/search"
    position_url = "http://lib.cqu.edu.cn/asset/getajaxpapercollection"
    detail_url = "http://lib.cqu.edu.cn/asset/detail/0/"

    def __init__(self, session: Session):
        self.session = session

    def fetch(self, keyword: str, page: int = 1, only_huxi: bool = False) -> List[Dict]:
        params = {
            'key': 'U=' + keyword,
            'cf': 'TY=1#图书[_]M=1#纸本馆藏' + ("[_]DL=虎溪图书馆@cqu#虎溪图书馆" if only_huxi else ''),
            'skey': '0_U_' + keyword,
            'page': str(page),
        }

        res = self.session.get(self.search_url, params=params)
        books = self.parse_search_html(res.text)
        self._get_book_position(books)
        return books

    def _get_book_position(self, books: List[Dict]):
        for book in books:
            book.update({'Pos': self.get_position_by_bid(self.session, book['BookId'])})

    @staticmethod
    def parse_search_html(html: str) -> List[Dict]:
        books = []
        soup = BeautifulSoup(html, features="html.parser")
        result = soup.find_all("dl", "book")

        for book in result:
            title_tag = book.find('a', 'title')
            book_id = book.find('div', 'source')['bookid']
            title = title_tag.text.strip().replace('\r\n', '').replace(u'\xa0', ' ')
            img_tag = book.find('img')
            img_url = img_tag['src'] if img_tag else None
            publisher_tags = book.find('dd', 'from').find_all('span')
            publisher = publisher_tags[0].text.strip()
            year = publisher_tags[-1].text.strip()
            author_str = book.find_all('dd', class_=False)[-1].text.strip()[3:].strip()
            authors = author_str.split('\n')
            introduction_element = book.find('dd', 'hideRemark')
            if introduction_element:
                introduction = introduction_element.find('span', 'abstract').text.strip()
            else:
                introduction = ''
            temp = {
                'BookId': book_id,
                'Title': title,
                'ImgUrl': img_url,
                'Publisher': publisher,
                'Year': year,
                'Authors': authors,
                'Introduction': introduction
            }
            books.append(temp)

        return books

    @staticmethod
    def parse_position_html(html: str) -> List[Dict]:
        soup = BeautifulSoup(html, features="html.parser")
        result = soup.find_all("tr")[1:]
        pos_list = []

        for item in result:
            tags = item.find_all("td")
            lib_name = tags[0].text
            lib_pos = tags[1].text
            book_sid = tags[3].text
            statue = tags[5].text
            if "在馆" in statue:
                statue = "在馆"
            else:
                statue = "已借出"
            temp = {
                'LibraryName': lib_name,
                'LibraryPosition': lib_pos,
                'BookSearchId': book_sid,
                'Statue': statue,
            }
            pos_list.append(temp)

        return pos_list

    @staticmethod
    def get_position_by_bid(session: Session, book_id: str) -> List[Dict]:
        params = {
            'bookid': book_id,
        }
        res = session.get(BookSearchSet.position_url, params=params)

        return BookSearchSet.parse_position_html(res.text)

    @staticmethod
    def parse_detail_html(html: str) -> Dict:
        soup = BeautifulSoup(html, features="html.parser")

        cover_tag = soup.find('div', 'cover').find('img')
        cover_url = cover_tag['src'] if cover_tag else None

        author_tag = soup.find('p', 'author')
        authors = []
        for author in author_tag.find_all('a'):
            authors.append(author.text.strip())

        detail = soup.find('div', 'article-detail')

        publisher = detail.find('p', 'from').a.text.strip()
        year_tag = detail.find_all('p', 'class')[0]
        introduction_tag = detail.find_all('p', 'abstrack')[-1]

        return {
            'Title': soup.find('div', class_='article-summary').find('h1')['title'],
            'ImgUrl': cover_url,
            'Publisher': publisher,
            'Year': [text for text in year_tag.stripped_strings][-1],
            'Authors': authors,
            'Introduction': [text for text in introduction_tag.stripped_strings][-1]
        }

    @staticmethod
    def get_book_detail(session: Session, book_id: str) -> Dict:
        res = session.get(BookSearchSet.detail_url + book_id)

        return BookSearchSet.parse_detail_html(res.text)

