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
        print("✓ Clicked Configure")
        time.sleep(4)
        
        # EEM Server button is in the same frame (eiamTopFrame)
        print("Looking for EEM Server button in current frame...")
        eem_server_btn = wait.until(
            EC.presence_of_element_located((By.ID, "hrefEEMServerConf"))
        )
        print("✓ Found EEM Server button")
        
        # Click using JavaScript
        print("Clicking 'EEM Server' button...")
        self.driver.execute_script("arguments[0].click();", eem_server_btn)
        print("✓ Clicked EEM Server")
        
        # Wait longer for the sidebar menu to load
        time.sleep(5)
        
        # Switch to main frame where the sidebar navigation is
        print("Switching to main frame for sidebar navigation...")
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("eiamMainFrame")
        print("✓ Switched to main frame")
        
        # Wait for the sidebar content to load
        print("Waiting for sidebar menu to load...")
        time.sleep(3)
        
        # Find Export Application link by its class and text
        print("Looking for 'Export Application' link...")
        
        try:
            # Method 1: Find by link text
            export_link = wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Export Application"))
            )
            print("✓ Found Export Application by link text")
        except:
            try:
                # Method 2: Find by partial link text
                export_link = wait.until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Export Application"))
                )
                print("✓ Found Export Application by partial link text")
            except:
                # Method 3: Find by CSS selector using the class
                export_link = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.sidenavsublink[href*='app_export']"))
                )
                print("✓ Found Export Application by CSS selector")
        
        # Scroll into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", export_link)
        time.sleep(1)
        
        # Click the link
        print("Clicking 'Export Application'...")
        export_link.click()
        print("✓ Clicked Export Application")
        time.sleep(4)
        
        return True
        
    except Exception as e:
        print(f"✗ Error during navigation: {str(e)}")
        
        # Enhanced debug information
        print("\nDEBUG INFO:")
        try:
            self.driver.switch_to.default_content()
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Print all available frames
            print("\nAvailable frames:")
            frames = self.driver.find_elements(By.TAG_NAME, "frame")
            for i, frame in enumerate(frames):
                frame_name = frame.get_attribute("name")
                frame_id = frame.get_attribute("id")
                print(f"  Frame {i}: name='{frame_name}', id='{frame_id}'")
            
            # Try to find the link in main frame and print what we find
            print("\nSearching for Export Application in eiamMainFrame:")
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame("eiamMainFrame")
                links = self.driver.find_elements(By.TAG_NAME, "a")
                print(f"  Found {len(links)} links in eiamMainFrame")
                for link in links[:10]:  # Print first 10 links
                    link_text = link.text.strip()
                    if link_text:
                        print(f"    - {link_text}")
            except Exception as debug_e:
                print(f"  Could not search frame: {debug_e}")
                
        except Exception as debug_error:
            print(f"Debug error: {debug_error}")
        
        self.driver.save_screenshot("error_navigation.png")
        print("Screenshot saved as: error_navigation.png")
        return False
