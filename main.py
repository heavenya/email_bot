import time
from collections import defaultdict

import datetime as datetime
import pytz
import us
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, TimeoutException
from threading import Thread
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

states = ['Alabama', 'Mississippi', 'Tennessee', 'Louisiana', 'Arkansas', 'South Carolina', 'West Virginia', 'Georgia',
          'Oklahoma', 'North Carolina', 'Texas', 'Utah', 'Kentucky', 'Virginia', 'Missouri', 'South Dakota', 'Ohio',
          'New Mexico', 'Iowa', 'Kansas', 'New Jerse', 'Florida', 'Indiana', 'Maryland', 'Nebraska', 'Wyoming',
          'Arizona',
          'District of Columbia', 'Michigan', 'North Dakota', 'Pennsylvania', 'Delaware', 'Idaho', 'Illinois',
          'California',
          'Minnesota', 'Nevada', 'Rhode Island', 'Montana', 'Oregon', 'Colorado', 'Hawaii', 'New York', 'Alaska',
          'Washington',
          'Wisconsin', 'Connecticut', 'Maine', 'Vermont', 'Massachusetts', 'New Hampshire'
          ]

base_url = "https://www.eventbrite.com/d/united-states--alabama/paid--spirituality--events/christian"

delay = 15

events_link = []

event_state_urls = defaultdict(list)

next_state_to_search = ''

FIRST_TIME = datetime.time(11, 00, 00)
SECOND_TIME = datetime.time(13, 00, 00)
THIRD_TIME = datetime.time(14, 00, 00)
FOURTH_TIME = datetime.time(16, 30, 00)


def calc_time_diff_in_secs(myTime, stateTime):
    """Calculates the time difference and returns delta in seconds"""
    delta = datetime.datetime.combine(datetime.date.today(), myTime) \
            - datetime.datetime.combine(datetime.date.today(), stateTime)
    if delta.total_seconds() <= 0:
        total_sec = delta.total_seconds() + 24 * 60 * 60
        in_hours = total_sec / 3600
        notify_slack_bot(message=f"Time to wait before sending: {in_hours} hour(s)")
        print('Time is less; adding up.. ' + str(delta.total_seconds() + 24 * 60 * 60))
        return total_sec
        # delta.total_seconds() + 24 * 60 * 60
    else:
        in_hours = delta.total_seconds() / 3600
        notify_slack_bot(message=f"Time to wait before sending: {in_hours} hour(s)")
        print('Time is okay; time to wait before sending: ' + str(delta.total_seconds()))
        return delta.total_seconds()
        # delta.total_seconds()


def notify_slack_bot(message, shot=None):
    """Sends a message and or screenshot to a Slack Channel"""
    client = WebClient(token=os.environ.get("ACCESS_TOKEN"))

    try:
        if shot is None:
            response = client.chat_meMessage(
                channel='#event-outreach-automation',
                text=message
            )
        else:
            filepath = str(shot) + '.png'
            response = client.files_upload(
                channels='#event-outreach-automation',
                title='Update',
                file=filepath,
                initial_comment=message
            )
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


class EventBriteMailingBot:

    def __init__(self):
        """Initialization"""
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=self.options)
        # self.driver = webdriver.Chrome(executable_path=r'c:\Users\david\chromedriver.exe')  # run this remotely

    def location_search(self):
        """Goes through states list, searching for events not in already searched csv"""
        global event_state_urls
        global events_link
        global next_state_to_search
        try:
            self.driver.get(base_url)
            location_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#locationPicker")
            ))
            location_elem.send_keys(Keys.CONTROL + 'a')
            time.sleep(delay)
            location_elem.send_keys(Keys.BACK_SPACE)
            time.sleep(delay)
            import csv

            state_in_csv_file = []
            with open('state_searched.csv', 'rt') as f:
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    for field in row:
                        state_in_csv_file.append(field)

            state_set = set(states)
            list_without = [item for item in state_set if item not in state_in_csv_file]
            next_state_to_search = list_without[0]
            time.sleep(delay)
            location_elem.send_keys(next_state_to_search)
            with open('state_searched.csv', 'a', newline='') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow([str(next_state_to_search)])

            time.sleep(delay)
            location_elem.send_keys(Keys.ENTER)
            print('Current state being searched: ' + str(next_state_to_search))
            notify_slack_bot(message='Current state being searched: ' + str(next_state_to_search))
            time.sleep(delay)
        except TimeoutException:
            notify_slack_bot(message="A network time out error 💔")
            print('A time out occurred while trying to search for events in a location')

    def find_events(self):
        """Locate and save event links in a page"""
        global next_state_to_search
        global event_state_urls
        global events_link

        try:
            event_url_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located(
                (By.XPATH,
                 "//*[@id='root']/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/div[1]/div/ul/li["
                 "*]/div/div/div[1]/div/div/div/article/div[2]/div/div/div[1]/a")
            ))
            time.sleep(delay)
            for link in event_url_elem:
                events_link.append(link.get_attribute('href'))
                event_state_urls[next_state_to_search].append(link.get_attribute('href'))
                print(link.get_attribute('href'))
            time.sleep(delay)

            while True:
                next_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                    (By.XPATH,
                     "//*[@id='root']/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/footer/div/div/ul/li[3]/button")
                ))
                event_url_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located(
                    (By.XPATH,
                     "//*[@id='root']/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/div[1]/div/ul/li["
                     "*]/div/div/div[1]/div/div/div/article/div[2]/div/div/div[1]/a")
                ))
                for link in event_url_elem:
                    events_link.append(link.get_attribute('href'))
                    event_state_urls[next_state_to_search].append(link.get_attribute('href'))
                    print(link.get_attribute('href'))  #
                time.sleep(delay)
                next_btn.click()
                time.sleep(delay)

        except StaleElementReferenceException:
            notify_slack_bot(message="Likely got to the end of page or something else 🤦‍")
            print('Likely got to the end of page or something else')
        except ElementNotInteractableException:
            notify_slack_bot(message="Likely got to the end of page or something else 🤦‍")
            print('Likely got to the end of page or something else')
        except TimeoutException:
            notify_slack_bot(message="A network time out error 💔")
            print('Time out occured')
        finally:
            event_state_urls[next_state_to_search] = events_link

    def open_event(self):
        """Checks the current timezone and time of the current location and calls send_mail function"""
        global events_link
        state_time_zone = us.states.lookup(str(next_state_to_search)).time_zones
        tzinf = pytz.timezone(state_time_zone[0])
        state_time = datetime.datetime.now(tzinf).time()
        day = datetime.datetime.now(tzinf).weekday()

        if day >= 5:
            notify_slack_bot(message=f'Im gonna sleep for 24 hours as today in {tzinf} is sunday or monday 😴🛌')
            print(f'Im gonna sleep for 24 hours as today in {tzinf} is Saturday or Sunday')
            time.sleep(24 * 60 * 60)
        else:
            time.sleep(calc_time_diff_in_secs(FIRST_TIME, state_time))
            self.send_email()
            time.sleep(calc_time_diff_in_secs(SECOND_TIME, state_time))
            self.send_email()
            time.sleep(calc_time_diff_in_secs(THIRD_TIME, state_time))
            self.send_email()
            time.sleep(calc_time_diff_in_secs(FOURTH_TIME, state_time))
            self.send_email()

    def send_email(self):
        """Goes through list, and sends (4) emails accordingly, sends a whatsapp message also"""
        urls_set = set(event_state_urls[next_state_to_search])
        print('Length in list: ' + str(len(event_state_urls[next_state_to_search])))
        print('Length in set: ' + str(len(urls_set)))
        for i, link in enumerate(urls_set):
            if (i + 1) <= 4:
                try:
                    self.driver.get(link)
                    event_name = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH,
                         "//*[@id='root']/div/div/div[2]/div/div/div/div[1]/div/main/div/div[2]/div/div[1]/div/div[2]/div/div[2]/h1")
                    )).text
                    contact_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR,
                         "#listings-root__organizer-panel > section > div.css-74fzkp > ul > li:nth-child(2) > button")
                    ))
                    time.sleep(delay)
                    contact_btn.click()
                    contact_org_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR,
                         "#edsModalContentChildren > main > section:nth-child(2) > div.eds-l-pad-top-3 > button")
                    ))

                    time.sleep(delay)
                    contact_org_btn.click()

                    time.sleep(delay)

                    name_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='name']")
                    ))
                    name_elem.send_keys('Travis Mitchell')

                    email_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='email']")
                    ))

                    email_elem.send_keys("event.promotion@heavenya.com")  # Todo: Replace with his mail
                    time.sleep(delay)

                    select_reason_elem = Select(self.driver.find_element(By.XPATH, "//*[@id='reason']"))
                    select_reason_elem.select_by_index(1)
                    message_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='message']")
                    ))
                    time.sleep(delay)
                    EMAIL_TEMPLATE = f"Hi my name is Travis Mitchell and was previously a nightclub promoter but after " \
                                     "becoming a Christian" \
                                     "I work at Heavenya where we promote Christian Events so more people in the area " \
                                     "show up. We would " \
                                     "like to promote the '({})'. Would you be open to discuss a collaboration " \
                                     "opportunity? "

                    message_elem.send_keys(EMAIL_TEMPLATE.format(event_name))

                    continue_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR,
                         "#event-page > div.contact-org-wrapper > div > div > div > div > div.eds-collapsible-pane-layout > div > div > main > div > div.eds-modal__footer-background > div > nav > div > button")
                    ))

                    continue_btn.click()
                    time.sleep(10)

                    submit_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR,
                         "#event-page > div.contact-org-wrapper > div > div > div > div > div.eds-collapsible-pane-layout > div > div > main > div > div.eds-modal__footer-background > div > nav > div > button")
                    ))
                    # Todo: make sure to enable the submit_btn

                    print('Waiting a while before opening another event')
                    screen_shot = self.driver.save_screenshot(str(i) + '.png')
                    time.sleep(delay)
                    message = '✅ Successfully contacted this event: ' + link
                    notify_slack_bot(message, i)
                    time.sleep(10)
                except TimeoutException:
                    print('There was a timeout')
                    screen_shot = self.driver.save_screenshot(str(i) + '.png')
                    time.sleep(delay)
                    message = '❌ An error occurred while contacting this event: ' + link
                    notify_slack_bot(message, screen_shot)


            else:
                try:
                    new_url_set = set()
                    for i in range(4):
                        print('popping off searched urls: ' + event_state_urls[next_state_to_search][i])
                        event_state_urls[next_state_to_search].pop(i)
                        urls_set.discard(event_state_urls[next_state_to_search][i])
                except IndexError:
                    print('calling myself again')
                break

    def save_events_mailed(self):
        """Save mailed events in a csv file"""
        pass

    def start(self):
        print('maximizing window')
        self.driver.maximize_window()
        print('Calling location_search()')
        self.location_search()
        print('calling find_events()')
        self.find_events()
        print('calling open_event()')
        self.open_event()
        print('done !')


if __name__ == '__main__':
    list_length = len(states)
    i = 0
    while True:
        if i <= list_length:
            print('Starting!')
            bot = EventBriteMailingBot()
            bot.start()
            i = i + 1
            print(i)
        else:
            print('Done')
