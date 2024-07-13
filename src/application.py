from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import pandas as pd
import os

import scrapers

def scrap_websites(driver: webdriver) -> pd.DataFrame:
    """Scrap the news for the given websites"""
    
    scraper_dict = {
        'G1': scrapers.G1NewsScraper(),
        'CNN': scrapers.CNNNewsScraper(),
        'UOL': scrapers.UolNewsScraper()
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


def save_output(news_df: pd.DataFrame):
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
        combined_df = pd.concat([existing_df, news_df]).drop_duplicates()
    else:
        combined_df = news_df

    # Save the combined DataFrame to the CSV file
    combined_df.to_csv(csv_file_path, index=False)


def main():
    # create the web driver
    GECKODRIVER_PATH = '/snap/bin/firefox.geckodriver'
    s = Service(executable_path=GECKODRIVER_PATH)
    # opens a window
    driver = webdriver.Firefox(service=s)
    try:
        # main routine for scraping
        news_df = scrap_websites(driver)
        
        save_output(news_df)
    finally:
        # assures the window is closed
        driver.quit()


if __name__ == '__main__':
    main()