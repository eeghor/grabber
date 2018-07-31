from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import calendar
import arrow
import time

import json


class Grabber:

	def __init__(self):

		# enable Allow Remote Automation in Develop menu in Safari
		self.driver = webdriver.Chrome('webdriver/chromedriver') #
		self.creds = json.load(open('creds/cdm.json'))
		self.BASE_URL = self.creds['base_url']

	def click_and_wait(self, element, secs=6):

		element.click()
		time.sleep(secs)

	def _find_by_text(self, tag_, class_, text_):

		for _ in self.driver.find_elements_by_css_selector(f'{tag_}.{class_}'):
			if _.text.strip().lower() == text_:
				return _

	def sign_in(self):

		print('signing in...')

		self.driver.get(self.BASE_URL)

		time.sleep(3)

		self.driver.set_window_size(1400, 1000)

		time.sleep(3)

		self.driver.find_element_by_xpath('//input[@id="identifierId"]').send_keys(self.creds['email'])

		time.sleep(2)

		next_button = self.driver.find_element_by_xpath('//*[@id="identifierNext"]/content/span')

		self.click_and_wait(next_button)

		self.driver.find_element_by_xpath('//input[@type="password"]').send_keys(self.creds['password'])

		time.sleep(2)

		next_button = self.driver.find_element_by_xpath('//*[@id="passwordNext"]/content/span')

		self.click_and_wait(next_button)

		# now it's asking about a code that's been sent to mobile
		code_ = input('please, enter your code: ')
		self.driver.find_element_by_xpath('//input[@id="idvPin"]').send_keys(code_)

		next_button = self.driver.find_element_by_xpath('//*[@id="idvPreregisteredPhoneNext"]/content/span')
		self.click_and_wait(next_button)

		google_icon = self.driver.find_element_by_css_selector('svg.Icon-google')
		self.click_and_wait(google_icon)

		print('successfully signed in')

		return self

	def _choose_database(self, db_name):
		"""
		click on the popover and choose database on the New question page
		"""

		select_database = self._find_by_text('span', 'text-grey-4', 'select a database')
		self.click_and_wait(select_database, secs=3)

		database_name = self._find_by_text('h4', 'List-item-title', db_name)
		self.click_and_wait(database_name, secs=3)

		return self

	def _run_query(self, q):
		"""
		run a query using the editor window on the New question page
		"""

		actions = ActionChains(self.driver)

		actions.move_to_element(self.driver.find_element_by_css_selector('div.ace_text-layer'))
		actions.click()
		actions.send_keys(q)
		actions.perform()

		get_answer_button = self.driver.find_element_by_css_selector('button.RunButton')
		self.click_and_wait(get_answer_button, secs=10)

		row_count = 0

		try:
			for _ in self.driver.find_element_by_css_selector('div.ShownRowCount').text.strip().split():
				if _.replace(',','').isdigit():
					row_count = int(_.replace(',',''))
					break
		except:
			print('cannot find row count!')

		print(f'got {row_count} rows')

		download_full_results = self.driver.find_element_by_css_selector('svg.Icon-downarrow')
		self.click_and_wait(download_full_results)

		csv_option = self._find_by_text('button', 'Button', 'csv')
		self.click_and_wait(csv_option)

		return self

	def run_question(self):

		# new_question = self._find_by_text('a', 'NavNewQuestion', 'new question')
		# self.click_and_wait(new_question)

		self.driver.get('https://metabase-test.seao-cdm.com/question/new')

		time.sleep(5)

		native_query = self._find_by_text('h2', 'transition-all', 'native query')
		self.click_and_wait(native_query)

		self._choose_database('gcdm')

		# [[1, 2, 3, 4, 5, 6, 7], 
		#  [8, 9, 10, 11, 12, 13, 14], 
		#  [15, 16, 17, 18, 19, 20, 21], 
		#  [22, 23, 24, 25, 26, 27, 28], 
		#  [29, 30, 31, 0, 0, 0, 0]]

		yr = 2018
		mnth = 1

		for wk in calendar.monthcalendar(yr,mnth):
			
			d0, d1 = arrow.get(f'{yr}-{mnth}-{min(wk)}').shift(days=-1).format('YYYY-MM-DD'), \
							arrow.get(f'{yr}-{mnth}-{max(wk)}').shift(days=+1).format('YYYY-MM-DD')

			q = f"""
					SELECT [gcdm.customers.id] AS [gcdm.customers.id], 
						[gcdm.customers.city] AS [gcdm.customers.city], 
						[gcdm.customers.country] AS [gcdm.customers.country], 
						[gcdm.customers.date_of_birth] AS [gcdm.customers.date_of_birth], 
						[gcdm.customers.gender] AS [gcdm.customers.gender], 
						[gcdm.customers.language] AS [gcdm.customers.language], 
						[gcdm.customers.last_ia_timestamp] AS [gcdm.customers.last_ia_timestamp], 
						[gcdm.customers.postcode] AS [gcdm.customers.postcode], 
						[gcdm.customers.region] AS [gcdm.customers.region]
					FROM [gcdm.customers] 
					WHERE (country = 'AU') and (DATE(last_ia_timestamp) > DATE(\'{d0}\')) and (DATE(last_ia_timestamp) < DATE(\'{d1}\'))
			"""

			self._run_query(q)

			print(f'got customers from between {d0} and {d1}...')

		return self


if __name__ == '__main__':

	g = Grabber().sign_in().run_question()