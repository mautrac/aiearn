import helium
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import selenium

INTERRUPT = -1
COMPLETE = 0
WRONG_PASSWORD = 1
RUNNING_ERROR = 2
LOGOUT_ERROR = 3

ALREADY_LOGIN = 4


def wait_page_complete(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    

def get_login_status(driver):
    account_str = driver.execute_script("return localStorage.getItem('account');")
    account = json.loads(account_str)

    return account['isLogin'], account['username']



def login(username, password, driver):
    helium.set_driver(driver)
    try:
        helium.go_to('https://aiearn.co/')

        helium.wait_until(helium.Button('Get Start').exists)
        helium.click('Get Start')

        helium.wait_until(helium.TextField('User ID').exists)
        helium.write(username, into='User ID')
        helium.write(password, into='Password')

        helium.click('Sign in')
        
        if helium.Text('Account or password error').exists():
            return WRONG_PASSWORD

        def check():
            if driver.current_url == 'https://aiearn.co/home/guess':
                return True
            return False
        try:
            helium.wait_until(check, timeout_secs=10, interval_secs=1)
        except Exception as inner_e:
            print("too long waiting login in")

    except Exception as e:
        raise e
    

def extract_time(driver):
    try:
        if driver.current_url != 'https://aiearn.co/home/vip':
            helium.go_to('https://aiearn.co/home/vip')
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
        if driver.current_url != 'https://aiearn.co/home/vip':
            raise Exception("redirected page")
        
        time.sleep(5)

        temp = driver.find_element(by=By.TAG_NAME, value='tbody')
        s = temp.find_element(By.XPATH, value='//tbody/tr[1]/td[1]/div').text

        return s
    
    except Exception as e:
        raise e



def get_point(driver):
    #helium.start_chrome('https://aiearn.co/')

    def wait():
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )


    def find_and_click():
        try:
            # Optional: scroll down if needed for lazy loading
            helium.scroll_down(2560)

            #helium.wait_until(helium.Image(below='Steal').exists)
            
            body = driver.find_element(By.TAG_NAME, 'tbody')
            image = body.find_element(By.XPATH, value='//tbody/tr[1]/td[4]/div/div')

            css = image.value_of_css_property('filter')
            if css == 'grayscale(1)':
                helium.click(image)
                return True
            
        except Exception as e:
            raise e

        return False
    

    def collect_point():
        pass

    def check_time():
        t = extract_time(driver)[3:].split(':')
        h = int(t[0])
        m = int(t[1])

        # if remaining time is less than 3:45, break
        if timedelta(hours=h, minutes=m) < timedelta(hours=3, minutes=45):
            return False
        return True

    try:
        # need to spam this operation every 60 seconds for 5 minutets
        it = 0
        while True and it < 5:
            try:
                helium.go_to('https://aiearn.co/home/vip')
                wait()
                if find_and_click():
                    break
                
            except Exception as inner_e:
                print(inner_e)
                raise Exception("Error while collecting point")
            
            it += 1
            try:
                if check_time() == False:
                    break
            except Exception as e:
                print("Error check time when collecting point")
            
            time.sleep(60)  # wait 60 seconds before repeating
            
    except Exception as e:
        raise e

    return COMPLETE


def log_out(driver):
    try:
        helium.go_to('https://aiearn.co/home/guess')
        time.sleep(5)
        # //*[@id="main-area"]/div[2]/div[3]/div/span
        # #main-area > div.css-sbw3ai > div.css-6ed3zy > div > span > img
        temp = driver.find_element(by=By.XPATH, value='//*[@id="main-area"]/div[2]/div[3]/div/span/img')
        helium.click(temp)
    except Exception as e:
        print("Can't find avatar icon")

    try:
        helium.wait_until('Sign out')
        helium.click('Sign out')
    except Exception as e:
        print(e)

    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception as e:
        print(e)
        
    
    #driver.get("about:blank")
    return COMPLETE