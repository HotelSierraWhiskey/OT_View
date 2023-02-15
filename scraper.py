import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class BaseOptions(Options):
    def __init__(self):
        super().__init__()
        self.add_experimental_option('detach', True)
        self.add_argument('--headless')
    

class ChromeDriver(webdriver.Chrome):
    def __init__(self):
        self.options = BaseOptions()
        super().__init__(service=Service(ChromeDriverManager().install()), options=self.options)


class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = ChromeDriver()
        self.schedule = None

    def launch(self):
        self.driver.get(self.url)

    def log_in(self, user_id, password):

        access_id = self.driver.find_element(By.ID, 'userId')
        access_id.send_keys(str(user_id))

        password_element = self.driver.find_element(By.ID, 'userPin')
        password_element.send_keys(password)
        
        submit_btn = self.driver.find_element(By.ID, 'submitBtn')
        submit_btn.click()

    def get_assignments(self):
        review_assignments = self.driver.find_element(By.ID, 'sidious.Review Assignments')
        review_assignments.click()

        search_btn = self.driver.find_element(By.ID, 'search')
        search_btn.click()

        body = self.driver.find_element(By.TAG_NAME, 'body')
        tbodies = body.find_elements(By.TAG_NAME, 'tbody')

        schedule = []

        def reformat_date(_dict, key):
            temp = _dict[key].split(' ')[0]
            temp = [int(i) for i in temp.split('/')]
            return (temp[2], temp[0], temp[1])

        for item in tbodies[3:]:
            t = item.text.strip()
            t = t.strip('\t')
            t = t.split('\n')

            entry = {
                'Job #': t[0].strip('Job # '),
                'Start Date/Time': t[1].replace('Start Date/Time ', ''),
                'End Date/Time': t[2].replace('End Date/Time ', ''),
                'Location': t[3].replace('Location ', ''),
                'Classification': t[4].replace('Classification ', ''),
                'Employee in for': t[5].replace('Employee in for ', ''),
                'Work Days': t[6].replace('Work Days ', ''),
            }
            
            entry['job_start_date'] = reformat_date(entry, 'Start Date/Time')
            entry['job_end_date'] = reformat_date(entry, 'End Date/Time')

            schedule.append(entry)
        self.schedule = schedule

    def write_json_schedule(self):
        if self.schedule:
            with open('data.json', 'w', encoding='utf-8') as file:
                json.dump(self.schedule, file, indent=4)
