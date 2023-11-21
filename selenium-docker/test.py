import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

print("Test Execution Started")
options = webdriver.ChromeOptions()
print("1")
options.add_argument('--ignore-ssl-errors=yes')
print("1")
options.add_argument('--ignore-certificate-errors')
print("1")
driver = webdriver.Remote(
command_executor='http://localhost:4444/wd/hub',
options=options
)
#maximize the window size
print("1")
driver.maximize_window()
time.sleep(3)
#navigate to browserstack.com
print("2")
driver.get("https://gaellevel.gumroad.com/")
time.sleep(3)
#click on the Get started for free button
print("3")
driver.find_element(By.CLASS_NAME, "icon icon-twitter").click()
time.sleep(3)
#close the browser
print("4")
driver.close()
driver.quit()
print("Test Execution Successfully Completed!")