import helium
import time
from selenium.webdriver.common.by import By

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apscheduler.triggers.base import BaseTrigger
from datetime import datetime, timedelta
import random


driver = helium.start_chrome()


def run(username, password):
    #helium.start_chrome('https://aiearn.co/')
    try:
        helium.go_to('https://aiearn.co/')

        helium.wait_until(helium.Button('Get Start').exists)
        helium.click('Get Start')

        helium.wait_until(helium.TextField('User ID').exists)
        helium.write(username, into='User ID')
        helium.write(password, into='Password')

        helium.click('Sign in')
        helium.wait_until(helium.Text('Recommend friends, you will get $10').exists)
        helium.go_to('https://aiearn.co/home/vip')

        helium.wait_until(helium.Image(below='Steal').exists)
        helium.click(helium.Image(below='Steal'))
    except Exception as e:
        print('Error at run function')
        print(e)


def log_out():
    try:
        temp = driver.find_element(by=By.CSS_SELECTOR, value='.chakra-stack.css-cp3a5l')
        temp = temp.find_element(by=By.CSS_SELECTOR, value='.chakra-avatar')
        temp = temp.find_element(by=By.TAG_NAME, value='img')

        helium.click(temp)

        # helium.wait_until('Sign out')
        helium.click('Sign out')

        helium.wait_until(helium.Button('Get Start').exists)
    except Exception as e:
        print("Log out error")
        print(e)


def get_time(username, password):
    try:
        run(username, password)
        s = driver.find_elements(by=By.CSS_SELECTOR, value='.chakra-text.css-0')[1].text.split(':')
        log_out()
        return int(s[0]), int(s[1])
    
    except Exception as e:
        print('get interval error')
        print(e)
        

def retrieve_intervals(accounts):
    intervals = []
    for acc in accounts:
        t = get_time(acc['username'], acc['password'])
        intervals.append(t)
    return intervals


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

# Example global or external config for interval (could be read from file/db)
def get_dynamic_interval():
    return random.randint(1, 5)  # Simulate dynamic hours (1 to 5)


class DynamicIntervalTrigger(BaseTrigger):
    def __init__(self, username, password):
        self._next_run_time = datetime.now()
        self.next_hour = 0
        self.next_minute = 0

        self.username = username
        self.password = password

    def get_next_fire_time(self, previous_fire_time, now):
        if previous_fire_time is None:
            return self._next_run_time

        # Determine the next interval dynamically
        interval = get_time(self.username, self.password)
        print(f'user: {self.username}  =next-time: {interval[0]} hours {interval[1]} minutes')
        return now + timedelta(hours=interval[0], minutes=interval[1])

    def __str__(self):
        return "<DynamicIntervalTrigger>"
    

def dummy_function():
    pass


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
                # args=[acc['username'], acc['password']],
                next_run_time=datetime.now()
            )

        scheduler.start()
    except Exception as e:
        print(e)
    finally:
        helium.kill_browser()

    

