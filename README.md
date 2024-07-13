# Brazilian news

This is a web scraping project that builds a dataset of the most recent news on the main news sites in Brazil. I choose [g1](https://g1.globo.com/), [uol](https://www.uol.com.br/) and [CNN Brasil](https://www.cnnbrasil.com.br/). 

It uses python with the librares selenium and BeaultifulSoup.

The main routine of scraping is in [application.py](src/scrapers.py)

I did some analysis with the resulting data, to show what is possible to do with this scraped data, in [data_analysis.ipynb](notebooks/data_analysis.ipynb).

![alt text](reports/figures/wordcloud.png)

**Important: This project was done in July 2024. The scraping code may not work anymore if the pages have major changes**

## How to run

You will need Python with the selenium, pandas and Beaultiful soup installed, as well as one [webdriver](https://www.selenium.dev/documentation/webdriver/) installed. Put the webdriver path and correct class into the main of [application.py](src/scrapers.py) . The application is then ready to run.