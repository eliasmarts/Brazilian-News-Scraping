from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import pandas as pd
import os
import logging

import scrapers

def create_logger():
    # create logger
    logger = logging.getLogger('scrap')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
    return logger

def scrap_websites(driver: webdriver, logger: logging.Logger) -> pd.DataFrame:
    """Scrap the news for the given websites"""
    
    scraper_dict = {
        'G1': scrapers.G1NewsScraper(logger=logger),
        'CNN': scrapers.CNNNewsScraper(logger=logger),
        'UOL': scrapers.UolNewsScraper(logger=logger)
    }
    
    scraped_news_dfs = []

    logger.info(f"Scraping websites {' '.join(scraper_dict.keys())}")
    # scrape all the websites
    for font, scraper in scraper_dict.items():
        try:
            news_df = scraper.scrap_news(driver)
            news_df['Font'] = font
            scraped_news_dfs.append(news_df)
        except Exception as e:
            logger.error(f"Error on scraping {font}: {e}")
        
    # create one dataframe with all the data
    news_df = pd.concat(scraped_news_dfs, axis='rows', join='outer', ignore_index=True)
    logger.info(f"Scraped all websites. Total news {len(news_df)}")
    return news_df


def save_output(news_df: pd.DataFrame, logger: logging.Logger):
    """ save on memory, appending the results to the anterior data saved
    """
    # Get the directory of the current file (application.py)
    current_dir = os.path.dirname(__file__)

    # Construct the path to the data folder
    data_folder = os.path.join(current_dir, '..', 'data')

    # Ensure the data folder exists
    os.makedirs(data_folder, exist_ok=True)

    # Define the path for the CSV file
    csv_file_path = os.path.join(data_folder, 'news.csv')
    
    # if the file already exists, merge dropping the duplicates
    if os.path.exists(csv_file_path):
        # Load the existing data
        existing_df = pd.read_csv(csv_file_path)
        
        # Merge the existing data with the new data
        combined_df = pd.concat([existing_df, news_df])
        
        duplicated_news = combined_df.duplicated(subset=['Title', 'Font']).sum()
        
        combined_df = combined_df.drop_duplicates(subset=['Title', 'Font'], keep='last')
        
        logger.info(f"{duplicated_news} news are already present on the dataset")
    else:
        combined_df = news_df

    # Save the combined DataFrame to the CSV file
    combined_df.to_csv(csv_file_path, index=False)
    
    logger.info(f"Sucess saving scraped data on {csv_file_path}")


def main():
    logger = create_logger()
    
    # create the web driver
    GECKODRIVER_PATH = '/snap/bin/firefox.geckodriver'
    s = Service(executable_path=GECKODRIVER_PATH)
    # opens a window
    logger.info("Starting webdriver")
    driver = webdriver.Firefox(service=s)
    
    try:
        # main routine for scraping
        news_df = scrap_websites(driver, logger)
        
        save_output(news_df, logger)
    finally:
        # assures the window is closed
        driver.quit()
        
    logger.info('Closed driver')

if __name__ == '__main__':
    main()