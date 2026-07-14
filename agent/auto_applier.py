from playwright.sync_api import sync_playwright
import time
import os

def apply_to_job(job_url: str, resume_path: str, first_name="Sumit", last_name="Togarshi", email="togarshisumit@gmail.com", phone="8217488690"):
    """
    Opens a visible Chrome browser and attempts to fill out a standard job application.
    Supports basic Greenhouse and Lever forms.
    """
    
    if not os.path.exists(resume_path):
        return f"❌ Error: Could not find your resume PDF at {resume_path}"

    try:
        with sync_playwright() as p:
            # headless=False means you can actually watch the bot click and type!
            browser = p.chromium.launch(headless=False, slow_mo=50) 
            page = browser.new_page()
            
            print(f"🤖 Navigating to {job_url}...")
            page.goto(job_url)
            
            # Wait for the page to load
            page.wait_for_load_state('networkidle')
            
            # 1. Fill out Name (Tries common ATS field names)
            print("🤖 Filling out personal info...")
            for selector in ['input[name="first_name"]', 'input[name="name"]', 'input[id="first_name"]']:
                if page.locator(selector).count() > 0:
                    page.fill(selector, first_name)
                    break
                    
            for selector in ['input[name="last_name"]', 'input[id="last_name"]']:
                if page.locator(selector).count() > 0:
                    page.fill(selector, last_name)
                    break
            
            # 2. Fill out Email
            for selector in ['input[name="email"]', 'input[type="email"]']:
                if page.locator(selector).count() > 0:
                    page.fill(selector, email)
                    break
                    
            # 3. Fill out Phone
            for selector in ['input[name="phone"]', 'input[type="tel"]']:
                if page.locator(selector).count() > 0:
                    page.fill(selector, phone)
                    break
            
            # 4. Upload Resume
            print("🤖 Uploading Resume...")
            file_inputs = page.locator('input[type="file"]')
            if file_inputs.count() > 0:
                # Usually the first file input is the resume
                file_inputs.nth(0).set_input_files(resume_path)
            
            print("✅ Form filled! Giving you 10 seconds to review before closing...")
            time.sleep(10) # Gives you time to review the bot's work and click submit yourself!
            
            browser.close()
            return "✅ Successfully filled out application! Check browser to submit."
            
    except Exception as e:
        return f"❌ Browser Automation Failed: {str(e)}"