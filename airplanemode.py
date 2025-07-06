from selenium import webdriver
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

driver = webdriver.Chrome()
driver.get("http://www.python.org")
assert "Python" in driver.title
