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
        
        # After clicking Configure, the EEM Server button appears in the TOP frame
        # We're already in eiamTopFrame, so no need to switch
        print("Looking for EEM Server button in current frame...")
        
        try:
            # Wait for EEM Server button to appear
            eem_server_btn = wait.until(
                EC.presence_of_element_located((By.ID, "hrefEEMServerConf"))
            )
            print("✓ Found EEM Server button")
            
            # Scroll to element if needed
            self.driver.execute_script("arguments[0].scrollIntoView(true);", eem_server_btn)
            time.sleep(1)
            
            # Click using JavaScript (more reliable for onclick handlers)
            print("Clicking 'EEM Server' button...")
            self.driver.execute_script("arguments[0].click();", eem_server_btn)
            print("✓ Clicked EEM Server")
            time.sleep(4)
            
        except Exception as e:
            print(f"Could not find in current frame, trying main frame...")
            # Fallback: try looking in main frame
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("eiamMainFrame")
            
            eem_server_btn = wait.until(
                EC.presence_of_element_located((By.ID, "hrefEEMServerConf"))
            )
            self.driver.execute_script("arguments[0].click();", eem_server_btn)
            print("✓ Clicked EEM Server from main frame")
            time.sleep(4)
        
        # Now switch to the main frame for Export Application
        print("Switching to main frame for Export Application...")
        self.driver.switch_to.default_content()
        
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("eiamMainFrame"))
            print("✓ Switched to main frame")
        except:
            print("! Main frame not available, staying in default content")
        
        # Wait for Export Application link
        print("Looking for 'Export Application' link...")
        time.sleep(3)
        
        # Try multiple strategies to find Export Application
        export_link = None
        try:
            # Try partial link text first
            export_link = wait.until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Export Application"))
            )
        except:
            # Try link text
            export_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Export Application"))
            )
        
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
                
        except Exception as debug_error:
            print(f"Debug error: {debug_error}")
        
        self.driver.save_screenshot("error_navigation.png")
        print("Screenshot saved as: error_navigation.png")
        return False
