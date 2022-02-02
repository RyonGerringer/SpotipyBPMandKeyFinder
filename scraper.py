from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os





def createHrefLink(artist):
    words = artist.split()
    
    link = '-'
    artist = link.join(words).lower()

    # wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'luke-combs')]")))

    resultFunc = f"driver.find_element_by_css_selector(\"a[href*='{artist}']\").get_attribute(\"textContent\")"
    waitFunc = f"wait.until(EC.presence_of_element_located((By.XPATH, \"//a[contains(@href, '{artist}')]\")))"
    return(resultFunc, waitFunc)
def findBPMandKey(song):
    artist = song[0]
    song_name = song[1]

    """options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)"""

   
    PATH = "chromedriver"
    #driver = webdriver.Chrome(PATH)
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=PATH, options=options)
    



    driver.get("https://songbpm.com/")



    # searches for the query name
    search = driver.find_element_by_name("query")
    search.send_keys(f"{artist} - {song_name}")
    search.send_keys(Keys.RETURN)
    key = ''
    bpm = ''


    # wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'luke-combs')]")))
    #driver.find_element_by_css_selector("a[href*='luke-combs']").get_attribute("textContent")


    try:
        resultFunc, waitFunc = createHrefLink(artist)
        print(resultFunc, waitFunc)
        wait = WebDriverWait(driver, 10)
        eval(waitFunc)
        result = eval(resultFunc)
        result = result.partition("Key")[2]
        key = result.partition("Duration")[0]
        bpm = result.partition("BPM")[2]

    except Exception as e:
        print(e)
        driver.quit()
        key = 'N/A'
        bpm = 'N/A'
    print()





    driver.quit()
    return key,bpm

