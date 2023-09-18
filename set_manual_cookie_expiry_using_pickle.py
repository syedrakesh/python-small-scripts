# INSTRUCTIONS TO RUN THIS SCRIPT
# Close Google Chrome
# Run This Command
# google-chrome --remote-debugging-port=9222
# Then Run This Python Script
# Will Generate A 'expedia-pickle.pkl' File In Same Directory
# Use This .pkl File To BOT For Logging In Into Any Application

import pickle
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime, timedelta


def set_manual_cookie_expiry(cookie, days=365):
    # Calculate the expiration date by adding days to the current date
    expiration_date = datetime.now() + timedelta(days=days)
    # Convert the expiration date to a Unix timestamp
    expiry = int(expiration_date.timestamp())

    # Set the expiry attribute of the cookie to the calculated timestamp
    cookie['expiry'] = expiry


def save_cookies_file(url):
    chrome_options = Options()
    chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Get the cookies from the browser
    cookies = driver.get_cookies()

    # Set a manual expiration date for each cookie (e.g. 365 days from now)
    for cookie in cookies:
        set_manual_cookie_expiry(cookie, days=365)

    # Save the modified cookies to a pickle file
    pickle.dump(cookies, open('expedia-pickle.pkl', 'wb'))


# Save cookies from the specified URL
save_cookies_file(
    'https://www.expediapartnercentral.com/Account/Logon?returnUrl=https%3A%2F%2Fapps.expediapartnercentral.com%2Flodging%2Fmultiproperty%2FMultiProperty.html')
