import logging
from selenium import webdriver

logging.basicConfig(level=logging.DEBUG)

print("Starting debug script...")
try:
    options = webdriver.EdgeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    print("Initializing driver...")
    driver = webdriver.Edge(options=options)
    print("Driver initialized successfully!")
    print("Current URL:", driver.current_url)
    driver.quit()
except Exception as e:
    print(f"Exception occurred: {e}")
