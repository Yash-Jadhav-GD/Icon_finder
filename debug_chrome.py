import logging
from selenium import webdriver

logging.basicConfig(level=logging.DEBUG)

print("Starting Chrome debug script...")
try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    print("Initializing driver...")
    driver = webdriver.Chrome(options=options)
    print("Driver initialized successfully!")
    print("Current URL:", driver.current_url)
    driver.quit()
except Exception as e:
    print(f"Exception occurred: {e}")
