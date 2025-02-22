import selenium
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta
import logging

import src.logging_config
logger = logging.getLogger(__name__)

class G1NewsScraper():
    """Scraper for the G1 news website"""

    def __init__(self, n_scrolls = 10):
        self.url = 'https://g1.globo.com/'
        
        # how many times to scrool the page
        self.n_scrolls = n_scrolls
        
        
    def _scroll_page(self, driver: selenium.webdriver):
        """Scroll the page by n_scrolls iterations"""
        
        logger.info(f"Scrolling page {self.n_scrolls} times")
        
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
            
            
            logger.debug(f"Scroll {i + 1}/{self.n_scrolls}. Height {current_height}")
            # time for the page to load
            sleep(4)
            
        logger.info(f"Scrolled to height {current_height}")

        
    def _get_scraped_news(self, driver: selenium.webdriver):
        """Obtain the scraped news from the website"""
        logger.info("Scraping data")
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # the news are split in many containers
        content_blocks = soup.find_all('div', class_ = '_evg') 
        
        highlight_area = soup.find('div', class_ = 'row small-collapse large-uncollapse')
        highlighted_news = highlight_area.find_all('ul', class_ = 'bstn-hl-list')
        
        titles = []
        times = []
        themes = []
        headers = []
        resumes = []
        highlight = []

        for hnews in highlighted_news:
            title = hnews.find('span', class_ = 'bstn-hl-title gui-color-primary gui-color-hover gui-color-primary-bg-after')
            titles.append(title.text)
            
            theme = hnews.find('span', class_ = 'bstn-hl-chapeu gui-subject gui-color-primary-bg-after')
            themes.append(None if theme is None else theme.text)

            # FIXME
            times.append('Há 1 minuto')

            resumes.append(None)
            headers.append(None)
            
            highlight.append(1)

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
                
                highlight.append(0)

        # create the final dataframe
        news_df = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Theme': themes,
            'Header': headers,
            'Resume': resumes,
            'Highlighted': highlight
        })
        
        logger.info(f"Sucess scraping {len(news_df)} news from {self.url}")
        
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
        
        logger.info(f"Loading {self.url}")
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
        logger.info(f"Scrolling page {self.n_scrolls} times")
        
        current_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1000)")

        for i in range(self.n_scrolls):
            # try to click in the 'Ver mais noticias' button
            try:
                driver.find_element(By.CSS_SELECTOR, value='.block-list-get-more-btn').click()
            except Exception:
                logger.warning(f"Unable to click on see more button")
            
            # scroll to the end of the page
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight - 1000)")
            current_height = driver.execute_script("return document.body.scrollHeight")
            
            
            logger.debug(f"Scroll {i + 1}/{self.n_scrolls}. Height {current_height}")
            # time for the page to load
            sleep(4)
            
        logger.info(f"Scrolled to height {current_height}")

    
    def _scrape_news_from_page(self, driver: selenium.webdriver, theme: str) -> pd.DataFrame:
        """Scrape the news of a given page (url/theme)"""

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        # one container contains all the news
        content_block = soup.find('div', class_ = 'col__l--9 col--12')
        news_list = content_block.find_all('li', class_ = 'home__list__item')
        
        highlight_area = soup.find('ul', class_ = 'three__highlights__list row')
        highlighted_news = highlight_area.find_all('div', class_ = 'three__highlights__titles')
        
        titles = []
        times = []
        themes = []
        highlight = []
        
        for hnews in highlighted_news:
            title = hnews.find('h2', class_ = 'block__news__title')
            titles.append(title.text)
            
            themes.append(theme)

            # FIXME
            times.append(datetime.now().strftime('%d/%m/%Y %H:%M'))

            highlight.append(1)
        
        for news in news_list:
            # obtain the data for a individual news
            title = news.find('h3', class_ = 'news-item-header__title')
            titles.append(title.text)

            time = news.find('span', 'home__title__date')
            times.append(None if time is None else time.text)
            
            themes.append(theme)
            
            highlight.append(0)
            
        data = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Theme': themes,
            'Highlighted': highlight
        })

        return data
    
    
    def _get_scraped_data(self, driver: selenium.webdriver) -> pd.DataFrame:
        """Scrape news for all the subpages in self.themes"""
        news_dfs = []

        for theme in self.themes:
            # scrape the page
            try:
                logger.info(f"Loading {self.url}{theme}")
                driver.get(f'{self.url}{theme}')
                sleep(5)
                
                self._scroll_page(driver)
                
                data = self._scrape_news_from_page(driver, theme)
                
                news_dfs.append(data)
            except Exception as e:
                logger.error(f"Error scraping {self.url}{theme}: {e}")
            
        # merge all the results of pages
        news_df = pd.concat(news_dfs, axis='rows')
        
        logger.info(f"Sucess scraping {len(news_df)} news from {self.url}")
        
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
        logger.info(f"Loading {self.url}")
        driver.get(self.url)
        
        news_df = self._get_scraped_data(driver)
        
        news_df = self._data_cleaning(news_df)
        
        return news_df
    
    
class UolNewsScraper():
    """Scraper for the UOL news website"""

    def __init__(self, n_scrolls = 10):
        self.url = 'https://noticias.uol.com.br/?clv3=true'
        
        # how many times to scrool the page
        self.n_scrolls = n_scrolls
        
        
    def _scroll_page(self, driver: selenium.webdriver):
        """Scroll the page by n_scrolls iterations"""
        logger.info(f"Scrolling page {self.n_scrolls} times")
        
        current_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(self.n_scrolls):
            # scroll to the end of the page
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            
            # if not autoload
            if new_height == current_height:
                # click the 'Veja mais' button
                driver.find_element(By.CSS_SELECTOR, value='.btn-search').click()
                
                # repeat the scroll
                driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight)")
                current_height = driver.execute_script("return document.body.scrollHeight")
            else:
                current_height = new_height
            
            logger.debug(f"Scroll {i + 1}/{self.n_scrolls}. Height {current_height}")
            # time for the page to load
            sleep(4)
            
        logger.info(f"Scrolled to height {current_height}")

        
    def _get_scraped_news(self, driver: selenium.webdriver):
        """Obtain the scraped news from the website"""
        logger.info("Scraping data")
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        
        content = soup.find('section', class_ = 'latest-news')
        news_list = content.find_all('div', class_ = 'thumb-caption')
        
        
        titles = []
        times = []
        resumes = []
        highlight = []
        
        # main header news
        titles.append(soup.find('h2').text)
        times.append(datetime.now().strftime('%d/%m/%Y %Hh%M'))
        resumes.append(None)
        highlight.append(1)

        for news in news_list:
            # obtain the info of a individual news
            title = news.find('h3', class_ = 'thumb-title')
            titles.append(title.text)

            time = news.find('time', class_ = 'thumb-date')
            times.append(None if time is None else time.text)

            resume = news.find('p', class_ = 'thumb-description')
            resumes.append(None if resume is None else resume.text)
            highlight.append(0)

        # create the final dataframe
        news_df = pd.DataFrame({
            'Title': titles,
            'Time': times,
            'Resume': resumes,
            'Highlighted': highlight
        })     

        logger.info(f"Sucess scraping {len(news_df)} news from {self.url}")
        
        return news_df
    
    def _convert_to_datetime(self, time_str: str) -> datetime:
        """Convert date in format  '13/07/2024 19h39' to datetime"""
        return datetime.strptime(time_str, '%d/%m/%Y %Hh%M')
        
    
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
        logger.info(f"Loading {self.url}")
        driver.get(self.url)
        sleep(1)
        
        self._scroll_page(driver)
        
        news_df = self._get_scraped_news(driver)
        
        news_df = self._data_cleaning(news_df)
        
        return news_df