# Brazilian news

This is a web scraping project that builds a dataset of the most recent news on the main news sites in Brazil. I choose [g1](https://g1.globo.com/), [uol](https://www.uol.com.br/) and [CNN Brasil](https://www.cnnbrasil.com.br/). 

It uses python with the librares selenium and BeaultifulSoup.

The main routine of scraping is in [application.py](src/scrapers.py)

I did some analysis with the resulting data, to show what is possible to do with this scraped data, in [data_analysis.ipynb](notebooks/data_analysis.ipynb).

Examples

![alt text](reports/figures/wordcloud.png)

Normal day with focus on political news

![alt text](reports/figures/wordcloud_trump.png)

Day after the attack to Donald Trump, and the final of the America Cup of soccer.

**Important: This project was done in July 2024. The scraping code may not work anymore if the pages have major changes**

## Resulting dataset
The extracted data is in [csv](data/news.csv). 

| Column       | Description                                                                                       |
|--------------|---------------------------------------------------------------------------------------------------|
| `Title`      | The title of the article.                                                                         |
| `Time`       | The publication timestamp of the article in the format `YYYY-MM-DD HH:MM:SS.SSSSSS`.              |
| `Theme`      | The category or theme of the article, such as "Economia" (Economy) or "Saúde" (Health).           |
| `Header`     | A brief summary or highlight of the article's main topic or content.                              |
| `Resume`     | A short description or abstract of the article, providing additional context or details.          |
| `Font`       | The sourcewhere the article was published (e.g., "G1").                           |
| `Highlighted`| A flag indicating whether the article is highlighted on the page (1 for highlighted, 0 for not highlighted).  |

Non avaliable data are marked with empty values

### Example Data

| Title                                                           | Time                          | Theme    | Header                        | Resume                                                                    | Font | Highlighted |
|-----------------------------------------------------------------|-------------------------------|----------|-------------------------------|---------------------------------------------------------------------------|------|-------------|
| Compras internacionais: 9 sites vão pagar imposto menor         | 2024-07-13 14:40:12.333107    | Economia | Itens de até US$ 50           | Empresas receberam certificado da Receita; outros 11 pedidos estão em análise. | G1   | 0           |
| Paciente espera há 3 anos pelo transplante de 5 órgãos          | 2024-07-13 04:23:12.333115    | Saúde    | Fila na Saúde                 |                                                                           | G1   | 0           |

Each row in the CSV represents a unique article with the above columns providing specific information about the article.


## How to run

You will need Python with the selenium, pandas and Beaultiful soup installed, as well as one [webdriver](https://www.selenium.dev/documentation/webdriver/) installed. Put the webdriver path and correct class into the main of [application.py](src/scrapers.py) .

The dependencies are listed in [environment.yml file](environment.yml) . To automatically create a conda environment to run this project, use **make create_environment**. You can also use any environment that has all the dependencies installed.