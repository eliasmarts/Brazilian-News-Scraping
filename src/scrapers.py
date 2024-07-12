import selenium
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta


class G1NewsScraper():
    def __init__(self):
        self.url = 'https://g1.globo.com/'
        
    def scroll_page(self, driver, n_scrolls):
        current_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(n_scrolls):
            # scroll to the end of the page
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            
            # if not autoload
            if new_height == current_height:
                # click the 'Veja mais' button
                driver.find_element(By.CSS_SELECTOR, value='.load-more > a:nth-child(1)').click()
                
                # repeat the scroll
                driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight)")
                current_height = driver.execute_script("return document.body.scrollHeight")
            else:
                current_height = new_height
                
            print(f'Scroll {i + 1}, height={current_height}')
            
            # time for the page to load
            sleep(4)
            
        
    def get_scraped_data(self, driver):
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        content_blocks = soup.find_all('div', class_ = '_evg')  
        
        titles = []
        times = []
        themes = []
        headers = []
        resumes = []

        for block in content_blocks:
            news_list = block.find_all('div', class_ = 'feed-post-body')
            for news in news_list:
                title = news.find('a', class_ = 'feed-post-link gui-color-primary gui-color-hover')
                titles.append(title.text)
                
                header = news.find('span', 'feed-post-header-chapeu')
                headers.append(None if header is None else header.text)

                time = news.find('span', 'feed-post-datetime')
                times.append(None if time is None else time.text)

                theme = news.find('span', 'feed-post-metadata-section')
                themes.append(None if theme is None else theme.text)

                resume = news.find('div', class_='feed-post-body-resumo')
                resumes.append(None if resume is None else resume.text)

                

        news_df = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Theme': themes,
            'Header': headers,
            'Resume': resumes
        })     
        
        return news_df
    
    def convert_to_datetime(self, time_str):
        """convert "Há X [time unit]" to datetime"""
        if 'hora' in time_str or 'horas' in time_str:
            hours_ago = int(time_str.split(' ')[1])
            return datetime.now() - timedelta(hours=hours_ago)
        
        elif 'minuto' in time_str or 'minutos' in time_str:
            minutes_ago = int(time_str.split(' ')[1])
            return datetime.now() - timedelta(minutes=minutes_ago)
        
        elif 'dia' in time_str or 'dias' in time_str:
            days_ago = int(time_str.split(' ')[1])
            return datetime.now() - timedelta(days=days_ago)
        
        elif 'mês' in time_str or 'meses' in time_str:
            months_ago = int(time_str.split(' ')[1])
            # Note: This is an approximation as timedelta does not support months directly
            return datetime.now() - timedelta(days=30*months_ago)
        else:
            return None  # If the format does not match, return None
        
    
    def data_cleaning(self, news_df):
        news_df['Time'] = news_df['Time'].apply(self.convert_to_datetime)
        return news_df

    def scrap_news(self, driver: selenium.webdriver):
        driver.get(self.url)
        sleep(1)
        
        self.scroll_page(driver, 10)
        
        news_df = self.get_scraped_data(driver)
        
        news_df = self.data_cleaning(news_df)
        
        return news_df
        
        
        
class CNNNewsScraper():
    def __init__(self):
        self.url = 'https://g1.globo.com/'
        
        
    def scroll_page(self, driver, n_scrolls):
        current_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(n_scrolls):
            # scroll to the end of the page
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)
            
            # handle the 'Aceitar Cokkies' popup
            # cookies_button = driver.find_elements(By.CSS_SELECTOR, value='#onetrust-reject-all-handler')
            # if cookies_button:
            #     cookies_button[0].click()
            #     sleep(1)
            
            try:
                driver.find_element(By.CSS_SELECTOR, value='.block-list-get-more-btn').click()
            except Exception:
                print('Error clicking')
            
            
            
            # repeat the scroll
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1000)")
            current_height = driver.execute_script("return document.body.scrollHeight")
                
            print(f'Scroll {i + 1}, height={current_height}')
            
            # time for the page to load
            sleep(4)
            
    
    def scrape_news_from_page(self, driver, theme):
        titles = []
        times = []
        themes = []

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        content_block = soup.find('div', class_ = 'col__l--9 col--12')
        news_list = content_block.find_all('li', class_ = 'home__list__item')
        
        for news in news_list:
            title = news.find('h3', class_ = 'news-item-header__title')
            titles.append(title.text)

            time = news.find('span', 'home__title__date')
            times.append(None if time is None else time.text)
            
            themes.append(theme)
            
        data = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Theme': themes
        })

        return data