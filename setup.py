from distutils.core import setup

setup(
  name = 'pygooglenewsscraper',
  packages = ['pygooglenewsscraper'],
  version = '0.1',
  license = 'MIT',
  description = 'Scrape news content from the Google News website',
  author = 'Shaheen Syed',
  author_email = 'shaheensyed15@gmail.com',
  url = 'https://github.com/shaheen-syed',
  download_url = 'https://github.com/shaheen-syed/pygooglenewsscraper/archive/refs/tags/v_0.1.tar.gz',
  keywords = ['web scraper', 'google news', 'parser', 'python', 'crawler'],
  install_requires=[
	  		'requests',
		  'trafilatura',
		  'beautifulsoup4',
	  ],
  classifiers=[
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.6',
  ],
)