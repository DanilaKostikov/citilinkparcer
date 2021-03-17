import requests
import bs4
import logging
import collections
import csv
import sys
import time
import random
import re
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

sys.setrecursionlimit(10**6)

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
        'article',
        'price',
        'popularity',
        'rating',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
    'Артикул',
    'Цена',
    'Популярность',
    'Оценка',
)

class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []
        self.number_of_products = 0

    def load_global_section(self, text: str):
        url = text
        res = self.session.get(url=url)
        res.raise_for_status()
        res = res.text
        soup = bs4.BeautifulSoup(res, 'lxml')
        container = soup.select('a.CatalogCategoryMenu__category')

        for block in container:
            url = block.get('href')
            url = url + '?view_type=list'
            logger.info(url)
            self.load_section(url)


    def load_section(self, text: str):
        time.sleep(random.randrange(0, 200, 1)/100)
        url_n = text
        try:
            res = self.session.get(url=url_n)
            res.raise_for_status()
        except Exception:
            return
        res = res.text
        soup = bs4.BeautifulSoup(res, 'lxml')
        container = soup.select('a.PaginationWidget__page.js--PaginationWidget__page.PaginationWidget__page_next.PaginationWidget__page-link')
        text_2 = self.load_page(url_n)
        self.pars_page(text=text_2)
        self.save_result()
        self.result = []
        logger.info(url_n)
        if container:
            container = container[0]
            url = container.get('href')
            soup = None
            container = None
            text_2 = None
            res = None
            gc.collect()
            return self.load_section(text=url)
        return

    def load_page(self, text: str):
        url = text
        res = self.session.get(url=url)
        res.raise_for_status()
        logger.debug(url)
        return res.text

    def pars_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product_data__gtm-js.product_data__pageevents-js.ProductCardHorizontal.js--ProductCardInListing.js--ProductCardInWishlist')
        for block in container:
            self.pars_block(block=block)
        container = None
        gc.collect()

    def pars_block(self, block):
        if block.select_one('ProductCardHorizontal__not-available-block') != None:
            return

        url_block = block.select_one('a.ProductCardHorizontal__title.Link.js--Link.Link_type_default')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no url')
            return

        logger.debug('%s', url)

        container = block.get('data-params')
        if not container:
            logger.error(f'no brand_name on {url}')
            return

        brand_name = re.findall(r'"brandName":"(.*?)",', container)
        brand_name = brand_name[0]

        logger.debug('%s', brand_name)

        goods_name = block.select_one('a.ProductCardHorizontal__title.Link.js--Link.Link_type_default')
        if not goods_name:
            logger.error(f'no goods_name on {url}')
            return

        goods_name = goods_name.get('title')

        logger.debug('%s', goods_name)

        container = block
        if container:
            container = container.get('data-product-id')
            articul = container
        else:
            articul = 'Артикула нет'

        logger.debug(articul)

        container = block
        if container:
            container = container.get('data-params')
            price = re.findall(r'"price":(.*?),', container)
            price = price[0]
            price = int(price)
        else:
            price = 'Цены нет'

        logger.debug(price)

        popularity = None

        logger.debug(popularity)

        container = block.select_one('span.ProductCardHorizontal__count.IconWithCount__count.js--IconWithCount__count')
        if container:
            rating = container.text
            rating = re.sub("[^0-9].", "", rating)
            rating = int(rating)
            rating = rating/5*10
        else:
            rating = 'Нет отзывов'

        logger.debug(rating)

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
            article=articul,
            price=price,
            popularity=popularity,
            rating=rating,
        ))

        logger.debug('-' * 100)

    def save_result(self):
        path = 'C:/Users/DanKos/PycharmProjects/citilinkparcer/citi.csv'
        with open(path, 'a', encoding='utf8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            for item in self.result:
                writer.writerow(item)
                self.number_of_products += 1
            logger.info(f'Товаров сохранено {self.number_of_products}')

    def run(self, text: str):
        self.load_global_section(text=text)


if __name__ == '__main__':
    parser = Client()
    parser.load_global_section('https://www.citilink.ru/catalog/smartfony-i-gadzhety/')
    parser.load_global_section('https://www.citilink.ru/catalog/noutbuki-i-kompyutery/')
    parser.load_global_section('https://www.citilink.ru/catalog/televizory-audio-video-hi-fi/')
    parser.load_global_section('https://www.citilink.ru/catalog/bytovaya-tehnika-dlya-doma-i-kuhni/')
    parser.load_global_section('https://www.citilink.ru/catalog/stroitelstvo-i-remont/')
    parser.load_global_section('https://www.citilink.ru/catalog/foto-video-sistemy-bezopasnosti/')
    parser.load_global_section('https://www.citilink.ru/catalog/avtotovary/')
    parser.load_global_section('https://www.citilink.ru/catalog/kanctovary-mebel-i-ofisnaya-tehnika/')
    parser.load_global_section('https://www.citilink.ru/catalog/krasota-i-zdorove/')
    parser.load_global_section('https://www.citilink.ru/catalog/detskie-tovary/')
    parser.load_global_section('https://www.citilink.ru/catalog/sport-i-otdyh/')
    parser.load_global_section('https://www.citilink.ru/catalog/tovary-dlya-geimerov/')
    parser.load_global_section('https://www.citilink.ru/catalog/dom-i-dacha/')
