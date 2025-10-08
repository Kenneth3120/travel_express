import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EEMLoginAutomation:
    def __init__(self):
        """Initialize the automation with configuration"""
        self.url = os.getenv('EEM_URL')
        self.username = os.getenv('EEM_USERNAME')
        self.password = os.getenv('EEM_PASSWORD')
        self.application = os.getenv('EEM_APPLICATION', 'WCC0004')
        self.driver = None
        
        # Path to manually downloaded EdgeDriver
        # UPDATE THIS PATH to where you saved msedgedriver.exe
        self.edge_driver_path = r"C:\EdgeDriver\msedgedriver.exe"
        
    def setup_driver(self):
        """Setup Edge WebDriver with options"""
        print("Setting up Edge WebDriver...")
        
        # Configure Edge options
        edge_options = EdgeOptions()
        # Uncomment the next line to run in headless mode (no browser window)
        # edge_options.add_argument('--headless')
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Handle SSL certificate issues (common in corporate environments)
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        
        # If you have proxy settings, uncomment and configure:
        # edge_options.add_argument('--proxy-server=http://proxy-address:port')
        
        # Initialize Edge driver with manual driver path
        service = EdgeService(executable_path=self.edge_driver_path)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        
        # Set implicit wait
        self.driver.implicitly_wait(10)
        print("WebDriver setup complete!")
        
    def login(self):
        """Perform login to EEM portal"""
        try:
            print(f"\nNavigating to: {self.url}")
            self.driver.get(self.url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for the login form to be present
            print("Waiting for login page to load...")
            wait.until(EC.presence_of_element_located((By.ID, "eiamUsername")))
            print("Login page loaded successfully!")
            
            # Select Application dropdown (if needed)
            print(f"\nSelecting application: {self.application}")
            application_dropdown = Select(self.driver.find_element(By.ID, "eiamApplication"))
            application_dropdown.select_by_visible_text(self.application)
            time.sleep(1)  # Brief pause after selection
            
            # Enter username
            print(f"Entering username: {self.username}")
            username_field = self.driver.find_element(By.ID, "eiamUsername")
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Enter password
            print("Entering password...")
            password_field = self.driver.find_element(By.ID, "eiamPassword")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            print("Clicking login button...")
            login_button = self.driver.find_element(By.ID, "btnSubmit1")
            login_button.click()
            
            # Wait for dashboard to load (adjust the wait condition based on dashboard page)
            print("\nWaiting for dashboard to load...")
            time.sleep(5)  # Give time for page transition
            
            # Check if login was successful
            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")
            
            if "login" not in current_url.lower() or "dashboard" in current_url.lower():
                print("✓ Login successful!")
                print(f"Page title: {self.driver.title}")
                return True
            else:
                print("✗ Login failed - still on login page")
                # Take screenshot for debugging
                self.driver.save_screenshot("login_error.png")
                print("Screenshot saved as login_error.png")
                return False
                
        except Exception as e:
            print(f"\n✗ Error during login: {str(e)}")
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot("error_screenshot.png")
                print("Error screenshot saved as error_screenshot.png")
            except:
                pass
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            print("\nClosing browser...")
            time.sleep(2)  # Brief pause to see the result
            self.driver.quit()
            print("Browser closed!")

def main():
    """Main execution function"""
    automation = EEMLoginAutomation()
    
    try:
        # Setup WebDriver
        automation.setup_driver()
        
        # Perform login
        success = automation.login()
        
        if success:
            print("\n" + "="*50)
            print("STEP 1 COMPLETE: Login automation successful!")
            print("="*50)
            input("\nPress Enter to close the browser...")
        else:
            print("\n" + "="*50)
            print("STEP 1 FAILED: Please check credentials and try again")
            print("="*50)
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        # Always close the browser
        automation.close()

if __name__ == "__main__":
    main()
