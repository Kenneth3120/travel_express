import os
import logging
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv

class SODAutomation:
    def __init__(self):
        """
        Initialize SOD Automation with paths and credentials.
        Edge driver path supplied by Jenkins (MS_EDGE_DRIVER_PATH) when the job runs on an agent.
        When running locally the original hard-coded path is kept as a fallback.
        """
        self.edge_driver_path = os.getenv('MS_EDGE_DRIVER_PATH', r'C:\59710\win64.exe')
        self.download_dir = os.path.join(os.getcwd(), 'downloads')
        self.screenshot_dir = os.path.join(os.getcwd(), 'Screenshots')
        self.email_report_path = os.path.join(os.getcwd(), 'SOD_Email_Report.html')
        
        # Dashboard URL
        self.dashboard_url = 'https://dynatrace-emea-core-02.cib.echonet/e/db0f9f42-ae38-4596-9033-1e6605ab2ae9/#dashboard;id=44648a45-7ffe-4cd8-880a-7'
        
        # Create directories if they don't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logging.info(f'Created download directory: {self.download_dir}')
        
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            logging.info(f'Created screenshot directory: {self.screenshot_dir}')
        
        # Load environment variables from .env file (username, password)
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        
        if not self.username or not self.password:
            logging.warning('USERNAME or PASSWORD not found in environment variables')
    
    def setup_driver(self):
        """Setup Edge WebDriver with optimal settings"""
        logging.info('Setting up Edge WebDriver...')
        print('Setting up Edge WebDriver...')
        
        edge_options = EdgeOptions()
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--no-sandbox')
        
        prefs = {
            'download.default_directory': self.download_dir,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        }
        edge_options.add_experimental_option('prefs', prefs)
        
        if not os.path.exists(self.edge_driver_path):
            logging.error(f'EdgeDriver executable not found at {self.edge_driver_path}')
            raise FileNotFoundError(f'EdgeDriver executable not found at {self.edge_driver_path}')
        
        service = EdgeService(executable_path=self.edge_driver_path)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.driver.implicitly_wait(20)
        
        logging.info('WebDriver setup complete!')
        print('WebDriver setup complete!')
        print(f'Downloads will be saved to: {self.download_dir}')
    
    def login(self):
        """Automate the login process and navigate to dashboard"""
        try:
            # Navigate to login page
            logging.info('Navigating to login page...')
            self.driver.get('https://dynatrace-emea-core-02.cib.echonet/login')
            print('Navigated to login page.')
            
            # Try to switch to iframe (if exists)
            try:
                iframe = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
                )
                self.driver.switch_to.frame(iframe)
                logging.info('Switched to iframe')
            except Exception:
                logging.info('No iframe found, continuing without switching')
            
            # Enter username
            logging.info('Entering credentials...')
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'user'))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'password'))
            )
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Click the sign-in button
            signin_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
            )
            signin_button.click()
            logging.info('Login submitted')
            print('Login submitted, waiting for redirect...')
            
            # Wait for redirect after login
            time.sleep(5)
            logging.info(f'Current URL after login: {self.driver.current_url}')
            
            # Navigate to the dashboard
            logging.info(f'Navigating to dashboard: {self.dashboard_url}')
            print('Navigating to dashboard...')
            self.driver.get(self.dashboard_url)
            
            # Wait for dashboard elements to load
            logging.info('Waiting for dashboard to load...')
            print('Waiting for dashboard to load...')
            
            try:
                # Wait for any dashboard element with ui-test-id attribute
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//span[@ui-test-id="gwt-debug-title"]'
                    ))
                )
                logging.info('Dashboard elements detected')
                print('Dashboard elements loaded')
            except Exception as e:
                logging.warning(f'Dashboard elements not immediately visible: {e}')
                print('Dashboard may still be loading, waiting additional time...')
            
            # Additional wait for all dynamic content to render
            time.sleep(10)
            
            # Take screenshot of the dashboard
            screenshot_path = os.path.join(self.screenshot_dir, 'screenshot.png')
            self.driver.save_screenshot(screenshot_path)
            logging.info(f'Screenshot saved to {screenshot_path}')
            print(f'Screenshot saved to {screenshot_path}')
            
        except Exception as e:
            logging.error(f'An error occurred during login: {e}')
            print(f'ERROR during login: {e}')
            self.driver.quit()
            raise
        
        return screenshot_path
    
    def extract_problem_counts(self):
        """Extract problem counts from the Dynatrace dashboard"""
        logging.info('Starting problem count extraction...')
        print('Extracting problem counts...')
        problem_counts = {}
        
        instances = {
            'EMEA - Autosys PROD France': '9557--AUTOSYS-UK-CIB--PRD',
            'UK': '9557--AUTOSYS-UK-CIB--PRD',
            'FR': '9558--AUTOSYS-FR-CIB--PRD',
            'NXT': '9559--AUTOSYS-NXT-CIB--PRD',
            'APAC-Autosys ITIP': '12236--AUTOSYS--PRD',
            'WMP': '12236--AUTOSYS--PRD',
            'ATLAS': '12236--AUTOSYS--PRD',
            'EMEA - Dollar U PROD': '8370--DOLLAR-UNI--PRD',
            'CIS': '8370--DOLLAR-UNI--PRD-CIS',
            'AMER - Autosys AMER': '4655--CA-AUTOSYS-US--PRD',
            'WAP PRD': '4655--CA-AUTOSYS-US--PRD',
            'DOLLAR U': '8370--DOLLAR-UNI--PRD',
            'DOLLAR U CIS': '8370--DOLLAR-UNI--PRD-CIS'
        }
        
        for instance, locator in instances.items():
            try:
                problem_count_element = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        f'//span[@ui-test-id="gwt-debug-title" and text()="{locator}"]'
                        f'/ancestor::div[@ui-test-id="gwt-debug-OPEN_PROBLEMS"]'
                        f'//span[@ui-test-id="gwt-debug-openCount"]'
                    ))
                )
                problem_count = problem_count_element.text
                problem_counts[instance] = problem_count
                logging.info(f'✓ Extracted problem count for {instance}: {problem_count}')
                print(f'  {instance}: {problem_count}')
            except Exception as e:
                logging.error(f'✗ Error extracting problem count for {instance}: {e}')
                print(f'  {instance}: Failed to extract (defaulting to 0)')
                problem_counts[instance] = '0'
        
        logging.info(f'Problem count extraction complete. Total instances: {len(problem_counts)}')
        print(f'Extraction complete: {len(problem_counts)} instances processed')
        return problem_counts
    
    def update_email_report(self, problem_counts, screenshot_path):
        """
        Generate an HTML email report with problem counts and a screenshot.
        If all counts are 0, overall status is OK, else KO.
        """
        logging.info('Generating email report...')
        print('Generating email report...')
        
        # Calculate total problems
        total_problems = sum(int(count) for count in problem_counts.values() if count.isdigit())
        
        # Determine overall status
        overall_status = 'OK' if total_problems == 0 else 'KO'
        
        logging.info(f'Total problems: {total_problems}, Overall status: {overall_status}')
        print(f'Total problems: {total_problems}')
        print(f'Overall status: {overall_status}')
        
        # Build table rows
        rows_html = ''
        for instance, count in problem_counts.items():
            status = 'OK' if count == '0' else 'KO'
            color = 'green' if status == 'OK' else 'red'
            rows_html += f'''
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{instance}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{count}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center; color: {color}; font-weight: bold;">{status}</td>
                </tr>
            '''
        
        # Encode screenshot to base64
        with open(screenshot_path, 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        
        # Build the full HTML report
        report_content = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                img {{ max-width: 100%; height: auto; margin-top: 20px; border: 1px solid #ddd; }}
                .status-ok {{ color: green; font-weight: bold; }}
                .status-ko {{ color: red; font-weight: bold; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h2>SOD Automation Report - {datetime.now().strftime('%d %B %Y')}</h2>
            <p><b>Overall Status: <span class="status-{'ok' if overall_status == 'OK' else 'ko'}">{overall_status}</span></b></p>
            <p><b>Total Problems Detected:</b> {total_problems}</p>
            
            <h3>Instance Status Summary</h3>
            <table>
                <tr>
                    <th>Instance</th>
                    <th style="text-align: center;">Problem Count</th>
                    <th style="text-align: center;">Status</th>
                </tr>
                {rows_html}
            </table>
            
            <h3>Dashboard Screenshot</h3>
            <img src="image/png;base64,{encoded_string}" alt="Dynatrace Dashboard Screenshot">
            
            <h3>Useful Links</h3>
            <ul>
                <li><a href="https://dynatrace-emea-core-02.cib.echonet/e/db0f9f42-ae38-4596-9033-1e6605ab2ae9/#dashboard;id=44648a45-7ffe-4cd8-880a-7">Dynatrace Dashboard</a></li>
                <li><a href="https://bnpp.service-now.com/now/nav/ui/classic/params/target/%24pa_dashboard.do">Global Scheduling Dashboard</a></li>
            </ul>
            
            <hr style="margin-top: 30px;">
            <p><b>Thanks and Regards,</b><br>
            Scheduling Team<br>
            BNP Paribas CIB IT Production</p>
            <p style="font-size: 11px; color: #666;">
                <i>This is an automated report generated by the SOD Automation System.</i>
            </p>
        </body>
        </html>
        '''
        
        # Write to file
        with open(self.email_report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logging.info(f'Email report saved to {self.email_report_path}')
        print(f'Email report saved to {self.email_report_path}')
        
        # Emit status line for Jenkins to parse
        print(f'STATUS : {overall_status}')
        
        return report_content
    
    def send_email(self, recipients, subject, body):
        """
        Log email details - Jenkins will handle the actual email sending
        """
        try:
            logging.info(f'Email prepared for: {", ".join(recipients)}')
            logging.info(f'Subject: {subject}')
            print('=' * 60)
            print('Email Report Prepared Successfully!')
            print(f'To: {", ".join(recipients)}')
            print(f'Subject: {subject}')
            print('Email will be sent by Jenkins')
            print('=' * 60)
        except Exception as e:
            logging.error(f'Error preparing email: {e}')
            print(f'Error preparing email: {e}')


# Main execution
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print('\n' + '=' * 60)
    print('SOD AUTOMATION SCRIPT - STARTING')
    print('=' * 60 + '\n')
    
    automation = SODAutomation()
    
    try:
        # Setup driver
        automation.setup_driver()
        
        # Login and navigate to dashboard
        screenshot_path = automation.login()
        
        # Extract problem counts
        problem_counts = automation.extract_problem_counts()
        
        # Generate email report
        report_html = automation.update_email_report(problem_counts, screenshot_path)
        
        # Prepare email (Jenkins will send it)
        recipients = ['kenneth.rebello@asia.bnpparibas.com']
        subject = f'FTS Scheduling SOD {datetime.now().strftime("%d %B %Y")}'
        body = report_html
        
        automation.send_email(recipients, subject, body)
        
        print('\n' + '=' * 60)
        print('SOD AUTOMATION COMPLETED SUCCESSFULLY!')
        print('=' * 60 + '\n')
        
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        print('\n' + '=' * 60)
        print(f'ERROR: {e}')
        print('=' * 60 + '\n')
        raise  # Re-raise to fail the Jenkins job
    finally:
        if hasattr(automation, 'driver'):
            automation.driver.quit()
            logging.info('Browser closed')
            print('Browser closed')