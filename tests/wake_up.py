from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def wake_up():
    print("Initializing headless browser...")
    
    # Configure Chrome options for headless environment
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Target URL
    url = "https://aeolianlux-concierge.streamlit.app/"
    
    try:
        print(f"Visiting {url}...")
        driver.get(url)
        
        # Wait for the app to actually load (connect via WebSocket)
        time.sleep(20) 
        
        print(f"Page Title: {driver.title}")
        print("Visit complete. App should be awake.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    wake_up()
