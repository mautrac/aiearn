import helium
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apscheduler.triggers.base import BaseTrigger
from datetime import datetime, timedelta, timezone
from apscheduler.util import astimezone

#import undetected_chromedriver as uc

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


from operations import *

# Set desired window size
width = 1920
height = 1080

# Create Chrome options
options = Options()
options.add_argument("--force-device-scale-factor=0.5")  # 1.25 = 125% zoom
options.add_argument(f"--window-size={width},{height}")
#options.add_argument("--headless=new")  # or just "--headless"
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")
options.add_argument('--enable-logging')
options.add_argument('--v=1')
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-accelerated-2d-canvas")

service = Service(
    #executable_path="chromedriver",  # or full path if not in PATH
    log_path="chromedriver.log"      # <-- this saves logs to a file
)

#driver = uc.Chrome(options=options)
# driver = helium.start_chrome(options=options)
# driver.set_page_load_timeout(60)
#helium.set_driver(driver)

def open_chrome():
    return webdriver.Chrome(service=service, options=options)


def read_accounts():
    accouts = []
    with open('./input.txt', 'r') as f:
        for line in f.readlines():
            temp = line.split(',')
            d = {
                'username': temp[0],
                'password': temp[1],
                'is_steal': bool(temp[2])
            }

            accouts.append(d)
    return accouts


class DynamicIntervalTrigger(BaseTrigger):
    def __init__(self, username, password):
        self._next_run_time = datetime.now()
        self.next_hour = 0
        self.next_minute = 0

        self.username = username
        self.password = password

    def get_next_fire_time(self, previous_fire_time, now):
        driver = open_chrome()
        driver.set_page_load_timeout(60)
        helium.set_driver(driver)

        # Determine the next interval dynamically

        print(f"-------RUNNING WITH USER: {self.username} ---------")

        attemp = 0
        while attemp < 5:
            try:
                flag = login(self.username, self.password, driver)
                if (flag == WRONG_PASSWORD):
                    print(f"WRONG PASSWORRD WITH USER: {self.username}")
                    return None
                elif flag == COMPLETE:
                    break

            except Exception as e:
                print(e)
                print("Re-attemp login")
                attemp += 1

        if attemp == 5:
            print("CAN'T LOGIN, USER: ", self.username, ". WILL RUN AGAIN IN 2 MINUTES")
            return datetime.now(timezone.utc) + timedelta(minutes=2)
        

        print("Login successfully")

        wait_page_complete(driver)

        attemp = 0
        print(f"Running get point")
        while attemp < 5:
            try:
                if (get_point(driver) == COMPLETE):
                    break

            except Exception as e:
                print(e)
                attemp += 1

                status = get_login_status(driver)
                # ->account['isLogin'], account['username']
                if status['isLogin'] == False:
                    print("INTERRUPTED WHILE RUNNING, WHILL TRY 10 MINUTES LATER!")
                    return datetime.now() + timedelta(minutes=10)
        
        if attemp == 5:
            print("CAN'T GET POINT, USER: ", self.username, ". WILL STOP THIS USER!")
            return None
                
        print(f"Got point")

        attemp = 0
        while attemp < 5:
            try:
                t = extract_time(driver).split(':')
                print("string got: ", t)
                h = int(t[0])
                m = int(t[1])
                break

            except Exception as e:
                print(e)
                attemp += 1

        if attemp == 5:
            print("CAN'T GET TIME, USER: ", self.username, ". WILL STOP THIS USER!")
            return None

        print("Got time")

        attemp = 0
        while attemp < 5:
            try:
                if (log_out(driver) == COMPLETE):
                    break
            except Exception as e:
                print(e)
                attemp += 1
        print("Logged out")
        
        if attemp == 5:
            raise Exception(f"CAN'T LOGOUT, USER: {self.username}")


        print(f'user: {self.username}  =next-time: {t[0]} hours {t[1]} minutes')
        helium.kill_browser()

        #now = astimezone(datetime.now())

        return datetime.now(timezone.utc) + timedelta(hours=h, minutes=m + 1)

    def __str__(self):
        return "<DynamicIntervalTrigger>"
    

def dummy_function(username, password):
    print(f"-------RUNNING:   {username}")


if __name__ == '__main__':
    try:
        accounts = read_accounts()
        # intervals = retrieve_intervals(accounts)

        scheduler = BlockingScheduler()
        

        for acc in accounts:
            di = DynamicIntervalTrigger(acc['username'], acc['password'])
            scheduler.add_job(
                dummy_function,
                trigger=di,
                args=[acc['username'], acc['password']],
                # next_run_time=datetime.now(),
                # id={acc['username']},
            )

        scheduler.start()
        
    except Exception as e:
        print(e)
    finally:
        try:
            driver = helium.get_driver()
            if driver:
                helium.kill_browser()
        except Exception:
            pass  # or log a warning

    

