import requests
import re
import logging
import datetime
import trafilatura
from bs4 import BeautifulSoup

class Request():

	def __init__(self, lang = 'en', country = 'US', timeout_sec = 60):
		
		self.lang = lang.lower()
		self.country = country.upper()
		self.http_header = self.set_http_header()
		self.cookies = self.set_cookies()
		self.timeout_sec = timeout_sec

	def set_http_header(self):
		""" Change header of a request so it looks like the request originates from an actual computer rather than a bot"""

		return {f"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15", 
				"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Language" : f"{self.lang}-{self.country},{self.lang};q=0.5"}

	def set_cookies(self):
		""" Cookies to try to accept/ignore accept or other consent popups/pages"""

		return {'BCPermissionLevel': 'PERSONAL',
				'CONSENT': 'YES+42'
				}

	
class GoogleNews(Request):

	def __init__(self, keyword, use_rss = False, use_quotes = True):
		super().__init__()
		# replace space with space character in html
		self.keyword = keyword.replace(' ', '%20') 
		# use rss feed or not
		self.use_rss = use_rss
		# basw url to scrape google news http website
		self.base_url = 'https://news.google.com'
		# use quotes from exact search match
		self.use_quotes = use_quotes
		# create url by adding the keyword to the News url, either base url or rss 
		self.url = self.create_url()

	def create_url(self):
		""" Create URL by adding the base url with the remaining url components including the keyword"""

		if self.use_quotes:
			return f'{self.base_url}/search/section/q/"{self.keyword}"'
		else:
			return f'{self.base_url}/search/section/q/{self.keyword}'

	def get_raw_news(self):
		""" Make a get request to retrieve the html content"""

		try:
			return requests.get(url = self.url, headers = self.http_header, cookies = self.cookies, timeout = self.timeout_sec)
		except Exception as e:
			print(e)
			return None

	def parse_news(self, html, invalid_href_terms = ["google", "youtube"]):
		"""Parse out news items with meta data"""

		# set html as attribute of Query
		self.html = html
	
		# to check if link is present
		links_checker = []
		# maintain a list of URL ID that Google used so we don't process the same twice
		links_ID_checker = []

		# create beautifulsoup object			
		bsObj = BeautifulSoup(self.html, "lxml")

		# create subset of html text that contain link data from link ID
		html_stripped = self.html.replace('\n', '')
		html_link_text = ""
		html_word_counter = 0
		for script in re.findall(r'<script.*?</script>' , html_stripped):				
			count = script.count('null')
			if count > html_word_counter:
				html_word_counter = count
				html_link_text = script

		# find all anchor, i.e. links
		valid_links = []
		for anchor in bsObj.findAll("a"):

			# check if the anchor is atttached to an image; we don't need them
			if len(anchor.findAll("img")) > 0:
				continue

			# find anchors with valid href
			try:
				href = anchor.attrs["href"]

				# check in url contains a link to google page such as google or youtube; we don't want them
				valid_url = True
				for invalid_term in invalid_href_terms:
					if invalid_term in href:
						logging.warning("Link contains invalid href term {}, skipping".format(invalid_term))
						valid_url = False

				# check if links contains invalid words
				if valid_url == True:
					# check if url starts with a dot or with a / => internal google links, we don't need them
					# if href.startswith("./articles/") and ('?' not in href): <- old method to find news articles urls.

					if href.startswith("./articles/"):

						"""
							For each news link Google provides an news links ID. The Url can then be traced back later in a script area with that link ID.
							Unfortunately, Google does not provide the link close to the original news title content
						"""
						try:
							# get the URL LINK ID + the unix time stemp
							link_id = re.search(r'/articles/(.*)', href).group(1)

							# delelete whatever comes after the link ID, for example ?hl=en-US&gl=US&ceid=US%3Aen
							link_id = re.sub(r'\?.*', '', link_id)

							if link_id not in links_ID_checker:
								# add to tracker
								links_ID_checker.append(link_id)
								# get URL text
								url_text_area = re.search(link_id + r'.*?"http.*?"', html_link_text).group(0)
								# get URL text area large
								url_text_area_large = re.search(link_id + r'.*' + link_id, html_link_text).group(0)				
								# get the URL
								url = re.search(r'"http.*?"', url_text_area).group(0).strip('"')
								
								logging.debug("Found URL: {}".format(url))

								# check if url contains invalid tokens
								valid_url = True
								for invalid_term in invalid_href_terms:
									if invalid_term in url:
										valid_url = False
										break
								# if not valid url then we need to skip it, for instance, if forbes or smartereum
								if not valid_url:
									logging.warning("Link contains invalid href term {}, skipping".format(invalid_term))
									continue

								"""
								Extract time stamp from script file that is located where we also extract the url from, that is in the scripts file below the page
								News articles do not always have the '4 weeks ago' text with the news, then the old method would find an incorrect time
								"""
								
								# get the unix time stamp
								time_stamp = re.search(r'\[[0-9]+\]',url_text_area).group(0)
								# strip the brackets
								time_stamp = time_stamp.lstrip('[').rstrip(']')
								logging.debug('Found time stamp: {}'.format(time_stamp))
								# convert unix time stamp
								datetime_datetime = datetime.datetime.fromtimestamp(int(time_stamp)).strftime('%Y-%m-%d')
								logging.debug('converted to datetime object : {}'.format(datetime_datetime))
								# save to variable
								url_date = str(datetime_datetime)

							else:
								logging.info("Link ID already processed: {}".format(link_id))
								continue
						except Exception as e:
							logging.error("Error retrieving url or time from from html content: {}".format(e))
							continue

						"""
							parse title
						"""
						try:
							link_title = re.search(link_id + r'"],"(.*?)","' ,url_text_area).group(1)
							logging.debug("Found link title: {}".format(link_title))
							if '|' in link_title:
								link_title = link_title.split('|')[0].strip()
								logging.debug('Updated link title: {}'.format(link_title))
						except Exception as e:
							logging.error("Error retrieving url publisher name: {}".format(e))
							continue

						"""
							parse publisher name
						"""
						try:
							publisher_name = re.search(r'Go to (.*?)"', url_text_area_large).group(1).strip()
							logging.debug("Found publisher's name: {}".format(publisher_name))
						except Exception as e:
							logging.error('Failed to extract publisher name from html content: {}'.format(e))
							publisher_name = None
						
						# save to list
						valid_links.append([link_title, url, publisher_name, url_date])

			except Exception as e:
				# logging.warning('Failed to extract valid href attribute: ' + str(e))
				continue

		logging.debug("Number of urls found: " + str(len(valid_links)))

		# return dictionary
		news_items = {}
		
		# add links to total list
		for link in valid_links:
			if link[1] not in links_checker:
				links_checker.append(link[1])
				# add to return dictionary
				news_items[link[1]] = {	'title' : link[0], 
										'url' : link[1], 
										'publisher' : link[2], 
										'date' : link[3],
										'datetime' : datetime.datetime.now()}

		return news_items


class NewsArticle(Request):

	def __init__(self, url):
		super().__init__()
		self.url = url
		self.raw_html = None
		self.content = None
		self.status_code = None
		self.timed_out = None
	
	def parse_main_content(self, include_comments = False, include_tables = False, allow_status_codes = [200]):
		"""
		Parse main content from website.
		"""

		try:
			
			# get html
			request = requests.get(url = self.url, headers = self.http_header, cookies = self.cookies, timeout = self.timeout_sec)
			# status code
			self.status_code = request.status_code
			
			if self.status_code in allow_status_codes:

				# raw html
				self.raw_html = request.text
				# get content of the main text
				self.content = trafilatura.extract(self.raw_html, include_comments = include_comments, include_tables = include_tables)

			else:
				logging.warning(f'Skipping status code {self.status_code}')
		
		except Exception as e:
			logging.error(e)
			self.timed_out = True
		
		return {'raw_html' : self.raw_html, 'content' : self.content, 'status_code' : self.status_code, 'timed_out' : self.timed_out, 'datetime' : datetime.datetime.now()}
			



