import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def login_and_download():
    # Setup standard Chrome options (no debugger port anymore)
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    print("Starting Chrome...")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        # Step 1: Go to the login page
        login_url = "https://www.magnific.com/log-in?client_id=magnific&lang=en"
        print(f"Navigating to login page: {login_url}")
        driver.get(login_url)
        
        print("Waiting for login form...")
        
        # We wait for the email input field to appear
        email_xpath = "//input[@type='email' or contains(@name, 'email') or contains(@id, 'email')]"
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, email_xpath)))
        
        print("Entering credentials...")
        email_input.send_keys("gep_ind_procurement@gep.com")
        
        # Let's wait for the password field to be interactable (some sites require clicking "Next" first, 
        # but if it's a standard form, it will be immediately available).
        password_xpath = "//input[@type='password' or contains(@name, 'password') or contains(@id, 'password')]"
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, password_xpath)))
        
        # If the password field is hidden, this might throw an error, but usually standard forms have them both on one page.
        password_input.send_keys("Pass#2026gep")
        
        # Submit the form by pressing ENTER on the password field (works on 99% of login forms)
        print("Submitting login form...")
        password_input.send_keys(Keys.RETURN)
        
        # Give the site a few seconds to process the login and redirect
        print("Waiting for login to complete...")
        time.sleep(7)
        
        # Step 2: Navigate to the specific icon download page
        icons_url = "https://www.magnific.com/author/freepik/icons/special-lineal_7?query=ai+chip"
        print(f"Navigating to icons page: {icons_url}")
        driver.get(icons_url)
        
        # Wait for the icon containers to appear
        container_selector = ".flex.aspect-square.w-full.items-center.justify-center"
        print(f"Waiting for icons to load on the page...")
        
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
        )
        
        # Get the total number of icons on the page
        initial_containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
        total_icons = len(initial_containers)
        print(f"Found {total_icons} icons on the page. Starting batch download...")
        
        for index in range(total_icons):
            try:
                print(f"\n--- Processing icon {index + 1} of {total_icons} ---")
                
                # Re-fetch all containers on every loop iteration to prevent StaleElementReferenceException
                containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
                if index >= len(containers):
                    print("Icon no longer exists on the page (index out of range). Skipping.")
                    continue
                    
                current_container = containers[index]
                
                # Close any open dropdowns or tooltips from the previous icon
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
                
                # Scroll the specific container into view instantly (smooth scrolling can cause race conditions)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_container)
                time.sleep(0.5) 
                
                # Hover over the container to make the download button visible
                print("Hovering over the icon container...")
                try:
                    # First try standard ActionChains hover
                    actions = ActionChains(driver)
                    actions.move_to_element(current_container).perform()
                except:
                    pass
                
                # Also force a JavaScript mouseover event just in case ActionChains is intercepted
                driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {'bubbles': true, 'cancelable': true, 'view': window}));", current_container)
                driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseenter', {'bubbles': true, 'cancelable': true, 'view': window}));", current_container)
                
                # Find the download button
                button_selector = "button[data-cy='download-icon-item']"
                
                # Retry loop to find the button (try for up to 5 seconds)
                download_button = None
                for _ in range(10):
                    try:
                        # 1. Try to find it inside the specific container
                        download_button = current_container.find_element(By.CSS_SELECTOR, button_selector)
                        if download_button.is_displayed():
                            break
                    except:
                        pass
                    
                    try:
                        # 2. If it's wrapped in a global Radix popper, search the whole page for the currently visible one
                        buttons = driver.find_elements(By.CSS_SELECTOR, button_selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                download_button = btn
                                break
                        if download_button:
                            break
                    except:
                        pass
                        
                    time.sleep(0.5)
                
                if not download_button:
                    print(f"Could not find download button for icon {index + 1} even after hovering, skipping.")
                    continue
                
                # Click the download button
                print("Clicking the download button...")
                try:
                    download_button.click()
                except Exception as e:
                    driver.execute_script("arguments[0].click();", download_button)
                    
                # Wait for the dropdown menu to appear in the DOM
                time.sleep(1.5) 
                
                # Find the SVG button (this is usually appended globally to the document body)
                print("Looking for the SVG option...")
                svg_xpath = "//*[normalize-space()='SVG']"
                
                try:
                    svg_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, svg_xpath))
                    )
                    
                    print("Clicking the SVG button...")
                    try:
                        svg_button.click()
                    except Exception as e:
                        try:
                            # Try ActionChains click if standard click is intercepted
                            ActionChains(driver).move_to_element(svg_button).click().perform()
                        except:
                            # Final fallback
                            driver.execute_script("arguments[0].click();", svg_button)
                            
                    print(f"Successfully triggered download for icon {index + 1}!")
                    
                except Exception as e:
                    print(f"Failed to find or click SVG for icon {index + 1}: {e}")
                
                # Wait a little bit between downloads to avoid getting blocked or overwhelming the browser
                time.sleep(2.5)
                
            except Exception as e:
                print(f"An unexpected error occurred while processing icon {index + 1}: {e}")
                # Continue with the next icon in the loop
        
        print("\nAll accessible icons have been processed!")
        time.sleep(5) # Final wait to ensure last downloads finish starting
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    login_and_download()
