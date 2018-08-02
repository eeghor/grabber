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

		# IMPORTANT: enable Allow Remote Automation in Develop menu in Safari if using Safari

		self.driver = webdriver.Chrome('webdriver/chromedriver') #
		self.creds = json.load(open('creds/cdm.json'))
		self.BASE_URL = self.creds['base_url']
		self.NEW_QUESTION_URL = 'https://metabase-test.seao-cdm.com/question/new'
		self.WINDOW_SIZE = (1400, 1000)

		self.rows_per_week = []

	def click_and_wait(self, element, secs=6):

		self.driver.execute_script("arguments[0].click();", element)
		# element.click()
		time.sleep(secs)

	def _find_by_text(self, tag_, class_, text_):
		"""
		find an element by text
		"""
		print(f'searching for {tag_}')

		wait = WebDriverWait(self.driver, 60)
		elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_)))


		print(len(elements))

		for _ in self.driver.find_elements_by_css_selector(f'{tag_}.{class_}'):
			if _.text.strip().lower() == text_:
				return _

	def sign_in(self):

		print('signing in...')

		self.driver.get(self.BASE_URL)

		time.sleep(3)

		self.driver.set_window_size(*self.WINDOW_SIZE)

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

		saved_current_url = self.driver.current_url

		while 1:

			try:
				self.click_and_wait(self._find_by_text('span', 'text-grey-4', 'select a database'), secs=8)
				self.click_and_wait(self._find_by_text('h4', 'List-item-title', db_name), secs=3)
				break
			except:
				self.driver.get(saved_current_url)
				time.sleep(5)

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
		self.click_and_wait(get_answer_button, secs=15)

		row_count = 0

		try:
			for _ in self.driver.find_element_by_css_selector('div.ShownRowCount').text.strip().split():
				if _.replace(',','').isdigit():
					row_count = int(_.replace(',',''))
					break
		except:
			print('cannot find row count!')

		print(f'got {row_count} rows')

		self.rows_per_week.append(row_count)

		download_full_results = self.driver.find_element_by_css_selector('svg.Icon-downarrow')
		self.click_and_wait(download_full_results)

		csv_option = self._find_by_text('button', 'Button', 'csv')
		self.click_and_wait(csv_option)

		return self

	def run_question(self, yr, mnth=None):

		
		if not mnth:
			months = range(1,13)
		else:
			months = range(mnth, mnth + 1)

		for m in months:

			print(self.rows_per_week)

			for i, wk in enumerate(calendar.monthcalendar(yr,m), 1):

				print(f'year {yr} month {m} week {i}...')

				# keep non-zero days only
				wk_ = [_ for _ in wk if _ > 0]
				

				d0 = arrow.get(f'{yr}-{m:02d}-{min(wk_):02d}').shift(days=-1).format('YYYY-MM-DD')
				d1 = arrow.get(f'{yr}-{m:02d}-{max(wk_):02d}').shift(days=+1).format('YYYY-MM-DD')

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

				self.driver.get(self.NEW_QUESTION_URL)
			
				time.sleep(5)
			
				if self.driver.current_url != self.NEW_QUESTION_URL:
					self.driver.get(self.NEW_QUESTION_URL)
					time.sleep(5)
			
				native_query = self._find_by_text('h2', 'transition-all', 'native query')
				self.click_and_wait(native_query)
			
				self._choose_database('gcdm')
				self._run_query(q)
	
		return self


if __name__ == '__main__':

	g = Grabber() \
			.sign_in() \
			.run_question(2017)