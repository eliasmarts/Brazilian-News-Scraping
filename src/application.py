from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import pandas as pd

import scrapers

def scrap_websites(driver: webdriver) -> pd.DataFrame:
    """Scrap the news for the given websites"""
    
    scraper_dict = {
        'G1': scrapers.G1NewsScraper(),
        'CNN': scrapers.CNNNewsScraper()
    }
    
    scraped_news_dfs = []

    # scrape all the websites
    for font, scraper in scraper_dict.items():
        news_df = scraper.scrap_news(driver)
        news_df['Font'] = font
        scraped_news_dfs.append(news_df)
        
    # create one dataframe with all the data
    news_df = pd.concat(scraped_news_dfs, axis='rows', join='outer', ignore_index=True)
    
    return news_df


def main():
    # create the web driver
    GECKODRIVER_PATH = '/snap/bin/firefox.geckodriver'
    s = Service(executable_path=GECKODRIVER_PATH)
    # opens a window
    driver = webdriver.Firefox(service=s)
    
    # main routine for scraping
    news_df = scrap_websites(driver)
    
    # save on memory
    # mode a append the results to the anterior data saved
    news_df.to_csv('../data/news.csv', mode='a')


if __name__ == '__main__':
    main()