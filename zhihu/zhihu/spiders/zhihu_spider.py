import scrapy
import pickle
import requests
import json
import re


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    topic = scrapy.Field()
    q_id = scrapy.Field()
    answer = scrapy.Field()


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"

    def start_requests(self):
        urls = [(topic,self.settings['START_URL_TMP'].format(topic=topic, mode=self.settings['MODE']))
                for topic in self.settings['TOPIC_ID_DICT'].values()]

        f = open(self.settings['COOKIE_PATH'], 'rb')
        cookie = pickle.load(f)
        f.close()
        my_cookies = requests.utils.dict_from_cookiejar(cookie)

        for topic, url in urls:
            item = ZhihuItem()
            item['topic'] = topic
            yield scrapy.Request(url=url, cookies=my_cookies, callback=self.parse,
                                 meta={'cookie': my_cookies,
                                       'item': item})

    # parse each question on the page, and go to next page if has any
    def parse(self, response):
        my_cookies = response.meta.get('cookie')
        item = response.meta.get('item')
        c = response.body.decode('utf-8')
        j = json.loads(c)

        for term in j['data']:
            q_id = term['target'].get('question', dict()).get('url')
            if q_id:
                q_id = q_id.split('/')[-1]
                item['q_id'] = q_id
                limit, offset = 10, 0
                q_url = 'https://www.zhihu.com/api/v4/questions/{q_id}/answers?include=data[' \
                        '*].content&limit={limit}&offset={offset}&platform=desktop&sort_by=default'.format(q_id=q_id,
                                                                                                           limit=limit,
                                                                                                           offset=offset)
                yield scrapy.Request(url=q_url, cookies=my_cookies, callback=self.parse_question_page,
                                     meta={'cookie': my_cookies,
                                           'item': item})

        next_page = j['paging'].get('next')
        if next_page or len(next_page) > 0:
            print('topic next page', next_page)
            yield scrapy.Request(url=next_page, cookies=my_cookies, callback=self.parse,
                                 meta={'cookie': my_cookies, 'item': item})

    # for question page, retrieve answers of current page, and go to next page if not end
    def parse_question_page(self, response):
        my_cookies = response.meta.get('cookie')
        item = response.meta.get('item')
        c = response.body.decode('utf-8')
        j = json.loads(c)

        # answers = []
        for answer in j.get('data', []):
            text_extract = ''.join(re.findall(r'\<p\>.*?\<\/p\>',answer.get('content')))
            item['answer'] = text_extract
            item['_id'] = answer['id']
            yield item

        # print('answer of current page: ', len(answers))
        if not j.get('paging', dict()).get('is_end', True):
            yield scrapy.Request(url=j['paging']['next'], cookies=my_cookies, callback=self.parse_question_page,
                                 meta={'cookie': my_cookies, 'item': item})
