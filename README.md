# pygooglenewsscraper
Scrape the news content from the Google news website (https://google.news.com).

It uses a keyword to retrieve the news title, URL, publisher, and date. The complete news content can then be retrieved from the URL.


## Examples

Retrieve Google News items through a search keyword

```python

# define keyword
keyword = 'artificial intelligence'

# google news object
googlenews = GoogleNews(keyword = keyword)

# perform google news search and retrieve raw news
raw_news = googlenews.get_raw_news()

# parse out the news articles
news = googlenews.parse_news(html = raw_news.text)

# print out results
for k, v in news.items():

	print(v['title'])
	print(v['url'])
	print(v['publisher'])
	print(v['date'])
	print()

```

Extract the news content for each URL

```python

# get main content of news items
for k, v in news.items():

	# news article object
	news_article = NewsArticle(url = v['url'])

	# parse out news
	news_content = news_article.parse_main_content()

	print(news_content['content'])

```

