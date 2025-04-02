from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      StaleElementReferenceException, 
                                      NoSuchElementException,
                                      WebDriverException)
from bs4 import BeautifulSoup
import time
import csv
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
MAX_WORKERS = 3  # Conservative to avoid blocking
INITIAL_URL = "https://www.imdb.com/search/title/?release_date=1995-01-01,&user_rating=6,10&num_votes=50000,"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def init_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.set_preference("permissions.default.image", 2)
    options.set_preference("general.useragent.override", USER_AGENT)
    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(45)
    return driver

def safe_get_element(parent, by, selector, default="N/A"):
    try:
        element = parent.find_element(by, selector)
        return element.text.strip()
    except:
        return default

def load_all_movies(driver):
    last_count = 0
    retries = 0
    
    while retries < 5:
        current_count = len(driver.find_elements(By.CSS_SELECTOR, "a.ipc-title-link-wrapper"))
        if current_count > last_count:
            last_count = current_count
            retries = 0
        else:
            retries += 1

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2 + random.random())
            
            buttons = driver.find_elements(By.CSS_SELECTOR, "button.ipc-see-more__button")
            if buttons:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", buttons[-1])
                driver.execute_script("arguments[0].click();", buttons[-1])
                time.sleep(2 + random.random())

        except Exception as e:
            print(f"Load error: {str(e)[:60]}")
            retries += 1

def get_movie_metadata(driver):
    """Extract metadata from main movie page with verified selectors"""
    metadata = {
        'title': safe_get_element(driver, By.CSS_SELECTOR, "h1[data-testid='hero__pageTitle']"),
        'year': 'N/A',
        'genres': [],
        'imdb_rating': 'N/A',
        'director': 'N/A',
        'cast': []
    }
    
    try:
        # Release year
        year_text = safe_get_element(driver, By.CSS_SELECTOR, "a[href*='releaseinfo']")
        metadata['year'] = re.search(r'\d{4}', year_text).group(0) if year_text else 'N/A'
        
        # Genres
        genre_elements = driver.find_elements(By.CSS_SELECTOR, "a.ipc-chip span.ipc-chip__text")
        metadata['genres'] = [g.text for g in genre_elements]

        # Rating
        rating_text = safe_get_element(driver, By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating__score'] span")
        metadata['imdb_rating'] = rating_text.split('/')[0] if rating_text else 'N/A'
        
        # Director
        metadata['director'] = safe_get_element(driver, By.XPATH, "//li[.//span[text()='Director']]//a[contains(@href, '/name/')]")
        
        # Cast (first 3)
        cast_elements = driver.find_elements(By.XPATH, "//a[contains(@data-testid, 'title-cast-item__actor')]")
        metadata['cast'] = [c.text for c in cast_elements[:3]]

    except Exception as e:
        print(f"Metadata error: {str(e)[:80]}")

    return metadata

def scrape_reviews(main_url):
    """Scrape reviews with verified 2024 IMDB structure"""
    driver = init_driver()
    reviews = []
    
    try:
        # Get main movie metadata
        driver.get(main_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        metadata = get_movie_metadata(driver)
        
        # Navigate to reviews page
        reviews_url = f"{main_url.rstrip('/')}/reviews/"
        driver.get(reviews_url)
        
        # Handle "All Reviews" expansion
        try:
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(., 'All Reviews')]]"))
            ).click()
            time.sleep(3)
        except TimeoutException:
            pass
        
        # Scroll to load reviews
        scroll_attempts = 0
        last_review_count = 0
        while scroll_attempts < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2.5 + random.random())
            
            # Check for new reviews
            containers = driver.find_elements(By.CSS_SELECTOR, "article.user-review-item")
            if len(containers) == last_review_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_review_count = len(containers)
            
            if len(containers) >= 25:
                break

        # Process reviews
        for container in containers:
            try:
                try:
                    spoiler_btn = container.find_element(
                        By.CSS_SELECTOR, 
                        "button.review-spoiler-button[aria-label='Expand Spoiler']"
                    )
                    driver.execute_script("arguments[0].click();", spoiler_btn)
                    time.sleep(0.5)  # Allow spoiler content to expand
                except NoSuchElementException:
                    pass

                # Get cleaned review text
                review_text = container.find_element(
                    By.CSS_SELECTOR, "div.ipc-html-content-inner-div").get_attribute('innerHTML')
                review_text = BeautifulSoup(review_text, 'html.parser').get_text('\n')
                review = {
                    **metadata,
                    'user_rating': safe_get_element(container, By.CSS_SELECTOR, "span.ipc-rating-star--rating", 'N/A').split()[0],
                    'review_text': review_text.strip(),
                    'helpful': parse_helpfulness(container)
                }
                reviews.append(review)
            except StaleElementReferenceException:
                continue

    except Exception as e:
        print(f"Error scraping {main_url}: {str(e)[:80]}")
    finally:
        driver.quit()
    
    return reviews

def parse_helpfulness(container):
    """Get thumbs up and total votes (up + down)"""
    try:
        up = convert_k(container.find_element(
            By.CSS_SELECTOR, 
            "span.ipc-voting__label__count--up"
        ).text)
        
        down = convert_k(container.find_element(
            By.CSS_SELECTOR,
            "span.ipc-voting__label__count--down"
        ).text)
        
        return f"{up}/{up + down}"
    
    except Exception as e:
        print(f"Helpfulness error: {str(e)[:80]}")
        return "0/0"


def convert_k(value):
    if 'K' in value:
        return int(float(value.replace('K', '')) * 1000)
    return int(value)

def main():
    driver = init_driver(headless=False)  # Disable headless for debugging
    
    try:
        print("Loading movies...")
        driver.get(INITIAL_URL)
        load_all_movies(driver)
        
        print("Extracting main movie links...")
        soup = BeautifulSoup(driver.page_source, "lxml")
        movie_links = [
            f"https://www.imdb.com{a['href'].split('?')[0]}"
            for a in soup.select('a.ipc-title-link-wrapper[href*="/title/tt"]')
        ]
        print(f"Total movies found: {len(movie_links)}")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(scrape_reviews, url): url 
                      for url in movie_links}
            
            with open('reviews.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'title', 'year', 'genres', 'imdb_rating',
                    'director', 'cast', 'user_rating', 'helpful', 'review_text'
                ])
                writer.writeheader()
                
                for i, future in enumerate(as_completed(futures), 1):
                    url = futures[future]
                    try:
                        result = future.result()
                        writer.writerows(result)
                        print(f"Processed {i}: {len(result)} reviews ({url})")
                        if len(result) == 0:
                            print("Zero reviews - check selectors manually!")
                    except Exception as e:
                        print(f"Failed {i}: {str(e)[:80]} ({url})")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()