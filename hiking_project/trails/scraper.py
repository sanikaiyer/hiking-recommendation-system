from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
import logging
from datetime import datetime

class CaliforniaTrailScraper:
    def __init__(self):
        logging.basicConfig(
            filename=f'trail_scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.options = webdriver.ChromeOptions()
        # Commenting out headless mode for debugging
        # self.options.add_argument('--headless=new')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
        self.trails_data = []
        # Updated URL to directly access the trails list
        self.base_url = "https://www.hikingproject.com/ajax/area/8007121/trails?limit=100&page=1"

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Timeout waiting for element: {value}")
            return None

    def get_trail_details(self, link):
        """Get detailed information from individual trail page"""
        try:
            self.driver.get(link)
            time.sleep(2)  # Wait for page to load
            
            # Extract detailed trail information
            name = self.wait_for_element(By.CSS_SELECTOR, "h1").text.strip()
            
            # Get difficulty
            difficulty_elem = self.wait_for_element(By.CSS_SELECTOR, "span.difficulty-circle")
            difficulty = difficulty_elem.text.strip() if difficulty_elem else "Not specified"
            
            # Get stats
            stats = {}
            stats_container = self.wait_for_element(By.CSS_SELECTOR, "div.trail-stats")
            if stats_container:
                stat_elements = stats_container.find_elements(By.CSS_SELECTOR, "div.mt-4")
                for stat in stat_elements:
                    try:
                        label = stat.find_element(By.CSS_SELECTOR, "div.text-xs").text.strip()
                        value = stat.find_element(By.CSS_SELECTOR, "div.text-base").text.strip()
                        stats[label] = value
                    except:
                        continue
            
            # Get description
            description_elem = self.wait_for_element(By.CSS_SELECTOR, "div.description-body")
            description = description_elem.text.strip() if description_elem else ""
            
            return {
                'name': name,
                'difficulty': difficulty,
                'stats': stats,
                'description': description,
                'link': link
            }
            
        except Exception as e:
            logging.error(f"Error getting trail details for {link}: {str(e)}")
            return None

    def scrape_trails(self):
        """Main function to scrape all trails"""
        try:
            # Start with the first page
            page = 1
            while True:
                url = f"https://www.hikingproject.com/ajax/area/8007121/trails?limit=100&page={page}"
                logging.info(f"Scraping page {page}: {url}")
                
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Check if we've reached the end of results
                if "No results found" in self.driver.page_source:
                    break
                
                # Find all trail links on the current page
                trail_links = self.driver.find_elements(By.CSS_SELECTOR, "a.link-color")
                
                if not trail_links:
                    break
                
                logging.info(f"Found {len(trail_links)} trails on page {page}")
                
                # Extract links before processing them (since we'll be navigating away from the page)
                links = [link.get_attribute('href') for link in trail_links]
                
                # Process each trail
                for link in links:
                    if link and 'trail' in link:
                        logging.info(f"Processing trail: {link}")
                        trail_info = self.get_trail_details(link)
                        
                        if trail_info:
                            self.trails_data.append(trail_info)
                            logging.info(f"Successfully scraped trail: {trail_info['name']}")
                        
                        time.sleep(1)  # Respectful delay between trails
                
                page += 1
                time.sleep(2)  # Delay between pages
            
            return self.trails_data
            
        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            self.driver.quit()

    def save_to_json(self, filename='california_trails.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.trails_data, f, indent=4, ensure_ascii=False)
        logging.info(f"Data saved to {filename}")

    def save_to_csv(self, filename='california_trails.csv'):
        if self.trails_data:
            df = pd.json_normalize(self.trails_data)
            df.to_csv(filename, index=False)
            logging.info(f"Data saved to {filename}")
        else:
            logging.error("No data to save to CSV")

def main():
    print("Starting trail scraper...")
    scraper = CaliforniaTrailScraper()
    print("Scraping trails (this may take several minutes)...")
    trails = scraper.scrape_trails()
    
    if trails:
        scraper.save_to_json()
        scraper.save_to_csv()
        print(f"Successfully scraped {len(trails)} trails")
        print("Data saved to 'california_trails.json' and 'california_trails.csv'")
    else:
        print("No trails were scraped. Check the log file for details.")

if __name__ == "__main__":
    main()