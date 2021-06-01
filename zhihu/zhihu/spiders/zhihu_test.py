# from DecryptLogin import login
# from DecryptLogin.utils.cookies import *
# from bs4 import BeautifulSoup
# import json
# import re
#
# username = 'lyxscraper1'
# password = '1reparcs_xyl'
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.115'}
# cookie_path = 'cookies.pkl'
# zhihu_home_paging_start_url = 'https://www.zhihu.com/api/v3/feed/topstory/recommend?page_number=1&limit=6&action' \
#                               '=down&after_id=1&ad_interval=-1 '
#
# zhihu_answers_paging_url_format = 'https://www.zhihu.com/api/v4/questions/{q_id}/answers?include=data[' \
#                                   '*].content&limit={limit}&offset={offset}&platform=desktop&sort_by=default '
#
# session = requests.Session()
# homepage_iteration = 10
# answers_page_iteration = 3
#
#
# def login_and_save_cookie(username, password):
#     lg = login.Login()
#     info_return, session = lg.zhihu(username=username, password=password)
#     saveSessionCookies(session=session, cookiespath='cookies.pkl')
#     return info_return
#
#
# def session_load_cookie(session, cookie_path):
#     f = open(cookie_path, 'rb')
#     session.cookies = pickle.load(f)
#     print(session.cookies)
#     # may need to check the validity of cookie
#     f.close()
#
#
# session_load_cookie(session, cookie_path)
#
#
# def scrape_from_home(response):
#     r_content = response.content.decode('utf-8')
#
#     soup = BeautifulSoup(r_content, features='lxml')
#     questions = soup.find_all("div", {"class": 'TopstoryItem'})
#     for q in questions:
#         link = q.a.get('href', '//')[2:]
#         print(link)
#         if link.startswith('www.zhihu.com/question'):
#             print('************************************************')
#             parse_questions(link.split('/')[2])
#         if link.startswith('zhuanlan.zhihu.com/p'):
#             print('************************************************')
#             parse_zhuanlan(link.split('/')[2])
#
#
# def scrape_from_home_paging(current_page_url, current_iteation=0):
#     response = session.get(current_page_url, headers=headers)
#
#     r_content = response.content.decode('utf-8')
#     # session_token_re = re.search(r'session_token[\s="\w]+', r_content, re.MULTILINE)
#     # session_token = session_token_re.group(0).split('=')[1]
#     j = json.loads(r_content)
#
#     for term in j['data']:
#         q_id = term['target'].get('question', dict()).get('url')
#         if q_id:
#             q_id = q_id.split('/')[-1]
#         else:
#             print(term)
#         print(q_id)
#         # parse_questions(q_id)
#
#     next_page = j['paging'].get('next')
#     if next_page:
#         scrape_from_home_paging(next_page, current_iteation+1)
#         current_iteation += 1
#         if current_iteation >= homepage_iteration: return
#
#
# def parse_zhuanlan(z_id):
#     print('zhuanlan: ', z_id)
#     z_url = 'http://zhuanlan.zhihu.com/p/' + z_id
#     response = session.get(z_url, headers=headers)
#     soup = BeautifulSoup(response.content.decode('utf-8'), features='lxml')
#     article = ''
#     for c in soup.find("div", {"class": "RichText"}).children:
#         if c.string:
#             article += c.string
#             article += '\n'
#     print(article)
#
#
# def parse_questions(q_id):
#     print('question: ', q_id)
#     paging_size = 20
#     offset = 0
#     answers = []
#
#     for i in range(answers_page_iteration):
#         paging_params = {"q_id": q_id, "offset": offset, "limit": paging_size}
#         paging_url = zhihu_answers_paging_url_format.format(**paging_params)
#         offset += paging_size
#
#         response = session.get(paging_url, headers=headers)
#         page = json.loads(response.content.decode('utf-8'))
#
#         for answer in page.get('data', []):
#             answers.append(answer.get('content'))
#
#         # Paging reach the end, done when collecting all answers from the question
#         if page.get('paging', dict()).get('is_end', True):
#             break
#
#     print(answers)
#
#
# # scrape_from_home_paging(337090932)
# parse_questions('337090932')
#
