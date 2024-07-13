import selenium
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta


class G1NewsScraper():
    """Scraper for the G1 news website"""

    def __init__(self, n_scrolls = 10):
        self.url = 'https://g1.globo.com/'
        
        # how many times to scrool the page
        self.n_scroll = n_scrolls
        
    def _scroll_page(self, driver: selenium.webdriver):
        """Scroll the page by n_scrolls iterations"""
        
        current_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(self.n_scrolls):
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
            
        
    def _get_scraped_news(self, driver: selenium.webdriver):
        """Obtain the scraped news from the website"""
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # the news are split in many containers
        content_blocks = soup.find_all('div', class_ = '_evg')  
        
        titles = []
        times = []
        themes = []
        headers = []
        resumes = []

        for block in content_blocks:
            news_list = block.find_all('div', class_ = 'feed-post-body')
            for news in news_list:
                # obtain the info of a individual news
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

        # create the final dataframe
        news_df = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Theme': themes,
            'Header': headers,
            'Resume': resumes
        })     
        
        return news_df
    
    def _convert_to_datetime(self, time_str: str) -> datetime:
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
        
    
    def _data_cleaning(self, news_df: pd.DataFrame):
        """Do simple data cleaning after the scrap"""
        news_df['Time'] = news_df['Time'].apply(self._convert_to_datetime)
        return news_df


    def scrap_news(self, driver: selenium.webdriver) -> pd.DataFrame:
        """Scrap the news for the G1 website

        Parameters
        ----------
        driver : selenium.webdriver
            Current webdriver

        Returns
        -------
        pd.DataFrame
            The news scraped
        """
        driver.get(self.url)
        sleep(1)
        
        self._scroll_page(driver)
        
        news_df = self._get_scraped_news(driver)
        
        news_df = self._data_cleaning(news_df)
        
        return news_df
        
        
        
class CNNNewsScraper():
    def __init__(self, n_scrolls = 10):
        self.url = 'https://www.cnnbrasil.com.br/'
        
        # the subpages to acess
        self.themes = ['politica', 'economia', 'esportes', 'pop']
        
        self.n_scrolls = n_scrolls
        
        
    def _scroll_page(self, driver):
        """Scroll the page by n_scrolls iterations"""
        current_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1000)")

        for i in range(self.n_scrolls):
            # try to click in the 'Ver mais noticias' button
            try:
                driver.find_element(By.CSS_SELECTOR, value='.block-list-get-more-btn').click()
            except Exception:
                print('Error clicking')
            
            # scroll to the end of the page
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1000)")
            current_height = driver.execute_script("return document.body.scrollHeight")
                
            print(f'Scroll {i + 1}, height={current_height}')
            
            # time for the page to load
            sleep(4)
            
    
    def _scrape_news_from_page(self, driver: selenium.webdriver, theme: str) -> pd.DataFrame:
        """Scrape the news of a given page (url/theme)"""

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # one container contains all the news
        content_block = soup.find('div', class_ = 'col__l--9 col--12')
        news_list = content_block.find_all('li', class_ = 'home__list__item')
        
        titles = []
        times = []
        themes = []
        
        for news in news_list:
            # obtain the data for a individual news
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
    
    
    def _get_scraped_data(self, driver: selenium.webdriver) -> pd.DataFrame:
        """Scrape news for all the subpages in self.themes"""
        news_dfs = []

        for theme in self.themes:
            # scrape the page
            driver.get(f'{self.url}{theme}')
            sleep(5)
            
            self._scroll_page(driver)
            
            data = self._scrape_news_from_page(driver, theme)
            
            news_dfs.append(data)
            
        # merge all the results of pages
        news_df = pd.concat(news_dfs, axis='rows')
        
        return news_df
    

    def _convert_to_datetime(self, time_str:str) -> datetime:
        """Convert date of format 'dd/MM/yyyy às HH:mm' to datetime"""
        # Remove the 'às' and strip any extra whitespace
        cleaned_str = time_str.strip().replace(' às ', ' ')
        # Convert to datetime using the appropriate format
        return datetime.strptime(cleaned_str, '%d/%m/%Y %H:%M')
        
        
    def _data_cleaning(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Do simple data cleaning after the scrap"""
        news_df['Time'] = news_df['Time'].apply(self._convert_to_datetime)

        news_df['Title'] = news_df['Title'].str.strip()
        
        return news_df
        

    def scrap_news(self, driver: selenium.webdriver) -> pd.DataFrame:
        """Scrap the news for the CNN website

        Parameters
        ----------
        driver : selenium.webdriver
            Current webdriver

        Returns
        -------
        pd.DataFrame
            The news scraped
        """
        driver.get(self.url)
        
        news_df = self._get_scraped_data(driver)
        
        news_df = self._data_cleaning(news_df)
        
        return news_df
        