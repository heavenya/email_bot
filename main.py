import time
from collections import defaultdict

import datetime as datetime
import pytz
import us
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, TimeoutException
from threading import Thread

states = ['Alabama', 'Mississippi', 'Tennessee', 'Louisiana', 'Arkansas', 'South Carolina', 'West Virginia', 'Georgia',
          'Oklahoma', 'North Carolina', 'Texas', 'Utah', 'Kentucky', 'Virginia', 'Missouri', 'South Dakota', 'Ohio',
          'New Mexico', 'Iowa', 'Kansas', 'New Jerse', 'Florida', 'Indiana', 'Maryland', 'Nebraska', 'Wyoming',
          'Arizona'
          'District of Columbia', 'Michigan', 'North Dakota', 'Pennsylvania', 'Delaware', 'Idaho', 'Illinois',
          'California',
          'Minnesota', 'Nevada', 'Rhode Island', 'Montana', 'Oregon', 'Colorado', 'Hawaii', 'New York', 'Alaska',
          'Washington',
          'Wisconsin', 'Connecticut', 'Maine', 'Vermont', 'Massachusetts', 'New Hampshire'
          ]

# list_lenght = range(len(states))

base_url = "https://www.eventbrite.com/d/united-states--alabama/paid--spirituality--events/christian"

delay = 10

events_link = []

event_state_urls = defaultdict(list)

next_state_to_search = ''

FIRST_TIME = datetime.time(11, 00, 00)
SECOND_TIME = datetime.time(13, 00, 00)  # use 24 hours format
THIRD_TIME = datetime.time(14, 00, 00)
FOURTH_TIME = datetime.time(16, 30, 00)


def calc_time_diff_in_secs(myTime, stateTime):
    """Calculates the time difference and returns delta in seconds"""
    delta = datetime.datetime.combine(datetime.date.today(), myTime) \
            - datetime.datetime.combine(datetime.date.today(), stateTime)
    if delta.total_seconds() <= 0:
        print('Time is less; adding up.. ' + str(delta.total_seconds() + 24 * 60 * 60))
        return 10
        # delta.total_seconds() + 24 * 60 * 60
    else:
        print('Time is okay; time to wait before sending: ' + str(delta.total_seconds()))
        return 10
        # delta.total_seconds()


class EventBriteMailingBot:

    def __init__(self):
        """Initialization"""
        self.driver = webdriver.Chrome(executable_path=r'c:\Users\david\chromedriver.exe')  # run this remotely

    def location_search(self):
        global event_state_urls
        global events_link
        global next_state_to_search
        """Goes through states list, searching for events not in already searched csv"""
        # Check if state has been searched before performing a search
        # if state has been searched make sure that all pages in the state has
        # been searched too.
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
        # add next_state_to_search to csv
        with open('state_searched.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow([str(next_state_to_search)])

        time.sleep(delay)
        location_elem.send_keys(Keys.ENTER)
        time.sleep(delay)

    def find_events(self):
        global next_state_to_search
        global event_state_urls
        global events_link
        """Find all events url and save in a list"""
        events_link = list()

        next_btn = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH,
             "//*[@id='root']/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/footer/div/div/ul/li[3]/button")
        ))

        try:
            while next_btn:
                mail_sent = 0
                event_url_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located(
                    (By.XPATH,
                     "//*[@id='root']/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/div[1]/div/ul/li["
                     "*]/div/div/div[1]/div/div/div/article/div[2]/div/div/div[1]/a")
                ))
                for link in event_url_elem:
                    events_link.append(link.get_attribute('href'))
                    # save in an outside list of dict
                    event_state_urls[next_state_to_search].append(link.get_attribute('href'))
                    print(link.get_attribute('href'))
                next_btn.click()
                time.sleep(delay)
        except StaleElementReferenceException:
            print('End of page')
        except ElementNotInteractableException:
            print('Wahala')
        except TimeoutException:
            print('Ewo, Time out error')
        finally:
            event_state_urls[next_state_to_search] = events_link

    def open_event(self):
        global events_link
        # Check current time of the state being searched, (have a global variable for
        # state that is currently being searched?
        #
        state_time_zone = us.states.lookup(next_state_to_search).time_zones
        tzinf = pytz.timezone(state_time_zone[0])
        state_time = datetime.datetime.now(tzinf).time()
        # while we havent gotten to the end of the list call send mail
        # to send 4 emails, then sleep till
        # if FIRST_TIME <= state_time:
        time.sleep(calc_time_diff_in_secs(FIRST_TIME, state_time))
        self.send_email()
        time.sleep(calc_time_diff_in_secs(SECOND_TIME, state_time))
        self.send_email()
        time.sleep(calc_time_diff_in_secs(THIRD_TIME, state_time))
        self.send_email()
        time.sleep(calc_time_diff_in_secs(FOURTH_TIME, state_time))
        self.send_email()
        # for url in events_link:
        #     i = 0
        #     while i <= 4:
        #         time_to_send_mail = calc_time_diff_in_secs(FIRST_TIME, state_time)
        #         time.sleep(time_to_send_mail)
        #         self.send_email()

        pass

    def send_email(self):
        """Goes through list, and sends (4) emails accordingly, sends a whatsapp message also"""
        # i = 0
        # while i <= 4 :
        #     hey = range(len(event_state_urls[next_state_to_search]))

        # for links in event_state_urls[next_state_to_search]:
        #     i = 0
        #     while i <= 4:
        #         # click through and send 4 mails
        #         pass
        for i, link in enumerate(event_state_urls[next_state_to_search]):
            if (i + 1) <= 4:
                # open a link and send mail
                try:
                    self.driver.get(link)
                    event_name = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH,
                         "//*[@id='root']/div/div/div[2]/div/div/div/div[1]/div/main/div/div[2]/div/div[1]/div/div[2]/div/div[2]/h1")
                    ))
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
                    name_elem.send_keys('Muna')

                    email_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='email']")
                    ))

                    email_elem.send_keys("boy@gmail.com")

                    select_reason_elem = Select(self.driver.find_element(By.XPATH, "//*[@id='reason']"))
                    select_reason_elem.select_by_index(1)
                    message_elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='message']")
                    ))
                    EMAIL_TEMPLATE = f"Hi my name is Travis Mitchell and was previously a nightclub promoter but after " \
                                     "becoming a Christian" \
                                     "I work at Heavenya where we promote Christian Events so more people in the area " \
                                     "show up. We would " \
                                     "like to promote the {event_name}. Would you be open to discuss a collaboration " \
                                     "opportunity? "

                    message_elem.send_keys(EMAIL_TEMPLATE.format(event_name=event_name.text))

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

                    print('Waiting a while before opening another event')
                    time.sleep(10)
                except TimeoutException:
                    print('There was a timeout, Chai')


            else:
                # delete first 4 items
                # write them in a csv file
                try:
                    for i in range(4):
                        print('popping off searched urls' + event_state_urls[next_state_to_search][i])
                        event_state_urls[next_state_to_search].pop(i)
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
        print('done !!!!!!!!!!!!!!!!! Joy !!!!!!!!!!!!!!!!!!!1')


if __name__ == '__main__':
    list_lenght = len(states)
    i = 0
    while True:
        if i <= list_lenght:
            print('Starting!')
            bot = EventBriteMailingBot()
            bot.start()
            i = i + 1
            print(i)
        else:
            print('Done')

# import datetime
#
# datetime.time(hour=11, minute=00, second=00)
# len(states)
