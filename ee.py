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

class EEMAutomation:
    def __init__(self):
        """Initialize the automation with configuration"""
        self.url = os.getenv('EEM_URL')
        self.username = os.getenv('EEM_USERNAME')
        self.password = os.getenv('EEM_PASSWORD')
        self.application = os.getenv('EEM_APPLICATION', 'WCC0004')
        self.driver = None
        
        # Path to manually downloaded EdgeDriver
        self.edge_driver_path = r"C:\EdgeDriver\msedgedriver.exe"
        
        # Download directory setup
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Created download directory: {self.download_dir}")
        
    def setup_driver(self):
        """Setup Edge WebDriver with download preferences"""
        print("Setting up Edge WebDriver...")
        
        # Configure Edge options
        edge_options = EdgeOptions()
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Handle SSL certificate issues
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        
        # Set download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        edge_options.add_experimental_option("prefs", prefs)
        
        # Initialize Edge driver
        service = EdgeService(executable_path=self.edge_driver_path)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        
        # Set implicit wait
        self.driver.implicitly_wait(10)
        print("WebDriver setup complete!")
        print(f"Downloads will be saved to: {self.download_dir}")
        
    def login(self):
        """Perform login to EEM portal"""
        try:
            print(f"\n{'='*60}")
            print("STEP 1: LOGIN")
            print('='*60)
            print(f"Navigating to: {self.url}")
            self.driver.get(self.url)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for login form
            print("Waiting for login page to load...")
            wait.until(EC.presence_of_element_located((By.ID, "eiamUsername")))
            print("✓ Login page loaded!")
            
            # Select Application dropdown
            print(f"Selecting application: {self.application}")
            application_dropdown = Select(self.driver.find_element(By.ID, "eiamApplication"))
            application_dropdown.select_by_visible_text(self.application)
            time.sleep(1)
            
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
            
            # Wait for dashboard
            print("Waiting for dashboard to load...")
            time.sleep(5)
            
            print("✓ Login successful!")
            return True
                
        except Exception as e:
            print(f"✗ Error during login: {str(e)}")
            self.driver.save_screenshot("error_login.png")
            return False
    
    def navigate_to_export(self):
        """Navigate through Configure -> EEM Server -> Export Application"""
        try:
            print(f"\n{'='*60}")
            print("STEP 2: NAVIGATE TO EXPORT")
            print('='*60)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Switch to top frame to find Configure button
            print("Switching to top frame...")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("eiamTopFrame")
            
            # Click Configure button
            print("Clicking 'Configure' button...")
            configure_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "hrefConfigure"))
            )
            configure_btn.click()
            time.sleep(2)
            print("✓ Clicked Configure")
            
            # Switch back to main frame
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("eiamMainFrame")
            
            # Click EEM Server
            print("Clicking 'EEM Server' button...")
            eem_server_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "hrefEEMServerConf"))
            )
            eem_server_btn.click()
            time.sleep(2)
            print("✓ Clicked EEM Server")
            
            # Click Export Application link
            print("Clicking 'Export Application' link...")
            export_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Export Application"))
            )
            export_link.click()
            time.sleep(3)
            print("✓ Clicked Export Application")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during navigation: {str(e)}")
            self.driver.save_screenshot("error_navigation.png")
            return False
    
    def configure_checkboxes(self):
        """Uncheck all boxes except Global Users and Policies"""
        try:
            print(f"\n{'='*60}")
            print("STEP 3: CONFIGURE CHECKBOXES")
            print('='*60)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Switch to details frame where checkboxes are located
            print("Switching to details frame...")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("eiamDetailsFrame")
            
            # Wait for checkboxes to load
            time.sleep(2)
            
            # Checkboxes to UNCHECK (these should be unchecked)
            checkboxes_to_uncheck = [
                "users",
                "globalusergroups",
                "usergroups",
                "globalfolders",
                "folders",
                "globalsettings",
                "calendars",
                "appobjects",
                "maxsearchsize"
            ]
            
            # Checkboxes to KEEP CHECKED
            checkboxes_to_check = [
                "globalusers",
                "policies"
            ]
            
            print("\nUnchecking unnecessary checkboxes...")
            for checkbox_id in checkboxes_to_uncheck:
                try:
                    checkbox = self.driver.find_element(By.ID, checkbox_id)
                    if checkbox.is_selected():
                        checkbox.click()
                        print(f"  ✓ Unchecked: {checkbox_id}")
                    else:
                        print(f"  - Already unchecked: {checkbox_id}")
                except Exception as e:
                    print(f"  ! Could not find checkbox: {checkbox_id}")
            
            print("\nEnsuring required checkboxes are checked...")
            for checkbox_id in checkboxes_to_check:
                try:
                    checkbox = self.driver.find_element(By.ID, checkbox_id)
                    if not checkbox.is_selected():
                        checkbox.click()
                        print(f"  ✓ Checked: {checkbox_id}")
                    else:
                        print(f"  - Already checked: {checkbox_id}")
                except Exception as e:
                    print(f"  ! Could not find checkbox: {checkbox_id}")
            
            print("\n✓ Checkbox configuration complete!")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"✗ Error configuring checkboxes: {str(e)}")
            self.driver.save_screenshot("error_checkboxes.png")
            return False
    
    def export_and_download(self):
        """Click Export button and wait for download to complete"""
        try:
            print(f"\n{'='*60}")
            print("STEP 4: EXPORT AND DOWNLOAD")
            print('='*60)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Get list of files before download
            files_before = set(os.listdir(self.download_dir))
            print(f"Files in download directory before: {len(files_before)}")
            
            # Click Export button
            print("Clicking 'Export' button...")
            export_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "btnExport1"))
            )
            export_btn.click()
            print("✓ Export button clicked!")
            
            # Wait for download to complete
            print("\nWaiting for file to download...")
            download_complete = False
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while not download_complete and (time.time() - start_time) < timeout:
                time.sleep(2)
                files_after = set(os.listdir(self.download_dir))
                new_files = files_after - files_before
                
                # Check if new file appeared and is not a temp file
                for file in new_files:
                    if not file.endswith('.crdownload') and not file.endswith('.tmp'):
                        print(f"✓ File downloaded: {file}")
                        download_complete = True
                        self.downloaded_file = file
                        break
                
                if not download_complete:
                    print("  Still downloading...", end='\r')
            
            if download_complete:
                print(f"\n✓ Download complete!")
                print(f"  File saved to: {os.path.join(self.download_dir, self.downloaded_file)}")
                return True
            else:
                print(f"\n✗ Download timeout after {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"✗ Error during export/download: {str(e)}")
            self.driver.save_screenshot("error_export.png")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            print("\n" + "="*60)
            print("Closing browser...")
            time.sleep(2)
            self.driver.quit()
            print("Browser closed!")

def main():
    """Main execution function"""
    automation = EEMAutomation()
    
    try:
        # Setup WebDriver
        automation.setup_driver()
        
        # Step 1: Login
        if not automation.login():
            print("\n✗ FAILED at Step 1: Login")
            return
        
        # Step 2: Navigate to Export
        if not automation.navigate_to_export():
            print("\n✗ FAILED at Step 2: Navigation")
            return
        
        # Step 3: Configure Checkboxes
        if not automation.configure_checkboxes():
            print("\n✗ FAILED at Step 3: Checkboxes")
            return
        
        # Step 4: Export and Download
        if not automation.export_and_download():
            print("\n✗ FAILED at Step 4: Export/Download")
            return
        
        # Success!
        print("\n" + "="*60)
        print("✓✓✓ AUTOMATION COMPLETED SUCCESSFULLY! ✓✓✓")
        print("="*60)
        print(f"\nDownloaded file location:")
        print(f"  {automation.download_dir}")
        
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
    finally:
        automation.close()

if __name__ == "__main__":
    main()
