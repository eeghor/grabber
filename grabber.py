from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import time

import json


class Grabber:

	def __init__(self):

		# enable Allow Remote Automation in Develop menu in Safari
		self.driver = webdriver.Safari() #

		self.creds = json.load(open('creds/cdm.json'))

		self.BASE_URL = self.creds['base_url']

	def click_and_wait(self, element, secs=6):

		element.click()

		time.sleep(secs)


	def sign_in(self):

		print('signing in...')

		self.driver.get(self.BASE_URL)

		time.sleep(3)

		self.driver.set_window_size(1200, 800)

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


	def navigate_to_table(self):

		try:
			data_reference = self.driver.find_element_by_xpath('//span[contains(text(), "Data Reference")]')
		except:
			# note that this one is always there but may be invisible
			data_reference = self.driver.find_element_by_css_selector('svg.Icon-reference')

		self.click_and_wait(data_reference)

		purple_button = self.driver.find_element_by_class_name('Button--purple')
		self.click_and_wait(purple_button)

		accounts = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3"]')

		self.click_and_wait(accounts)

		tables_in_samsung_accounts = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3/tables"]')

		self.click_and_wait(tables_in_samsung_accounts)

		customer_phones = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3/tables/10"]')
		self.click_and_wait(customer_phones)

		see_this_table = self.driver.find_element_by_css_selector('span.mr1.flex-no-shrink')
		self.click_and_wait(see_this_table, secs=8)

		view_sql_button = self.driver.find_element_by_css_selector('svg.Icon-sql')
		self.click_and_wait(view_sql_button)

		self.driver.switch_to.active_element

		convert_to_sql_button = self.driver.find_element_by_css_selector('a.Button--primary')
		self.click_and_wait(convert_to_sql_button, secs=8)

		try:
			textarea = WebDriverWait(self.driver, 30).until(EC.visibility_of(By.CLASS_NAME, "ace_text-input"))
		finally:
			print('done')

		textarea.clear()

		a_ = 'samsung_accounts.customer_phones'

		q = f"""
			SELECT [{a_}.age_bucket] AS age_group, 
					[{a_}.carrier] AS carrier, 
					[{a_}.category] AS category, 
					[{a_}.country] AS country, 
					[{a_}.first_seen] AS first_seen, 
					[{a_}.gender] AS gender,
					[{a_}.is_opted_in] AS is_opted_in, 
					[{a_}.language] AS language, 
					[{a_}.model] AS model, 
					[{a_}.number_of_devices] AS number_of_devices, 
					[{a_}.registration_date] AS registration_date,
					[{a_}.samsung_account_id] AS account_id,
					[{a_}.series] AS series
			FROM [{a_}] 
					WHERE (country = 'AUS') AND (age_bucket = '36-45') AND (DATE(first_seen) > DATE('2012-01-01')) AND (DATE(first_seen) < DATE('2012-02-01'))
			"""

		textarea.send_keys(q)

		get_answer_button = self.driver.find_element_by_css_selector('button.RunButton')
		self.click_and_wait(get_answer_button, secs=10)

		download_full_results = self.driver.find_element_by_css_selector('svg.Icon-downarrow')
		self.click_and_wait(download_full_results)

		choose_csv = self.driver.find_element_by_xpath('/html/body/span[11]/span/div/div/div/form[1]/button')
		self.click_and_wait(choose_csv)

		return self



if __name__ == '__main__':

	g = Grabber().sign_in().navigate_to_table()