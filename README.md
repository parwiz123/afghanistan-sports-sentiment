# Afghanistan Sports Sentiment Analysis

##  Project Overview
This project scrapes sports news articles related to Afghanistan and performs sentiment analysis using NLP and machine learning models.

The goal is to understand how Afghanistan’s national sports teams are represented in news articles.

---

## Pipeline

### 1. Web Scraping
- Used `Playwright` and `BeautifulSoup`
- Scraped ~80 pages from Ariana News
- Extracted article **title, text, and URL**

### 2. Data Filtering
- Kept only **Afghanistan national team sports news**
- Removed irrelevant or local sports content

### 3. Models
- Created Logisitic Regression Model
- Created Random Forest Classifier

