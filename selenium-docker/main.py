from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os

url = os.getenv("LT_HUB_URL")

options = webdriver.ChromeOptions()
options.browser_version = '116.0'
options.platform_name = 'Windows 11'
cloud_options = {}
cloud_options['build'] = os.getenv("LT_BUILD_NAME")
cloud_options['name'] = 'test'
options.set_capability('cloud:options', cloud_options)
driver = webdriver.Remote(url, options=options)

driver.get("http://localhost:56733/signup")
driver.quit()
