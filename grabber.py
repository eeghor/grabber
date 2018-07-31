from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import calendar

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


	def navigate_to_table(self):

		print('starting new question...')

		new_question = self.driver.find_element_by_css_selector('a.NavNewQuestion')
		self.click_and_wait(new_question)

		native_query = self.driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/ol/li[2]/a/div[1]/img')
		self.click_and_wait(native_query)

		for s in self.driver.find_elements_by_css_selector('span.text-grey-4'):
			if s.text.lower().strip() == 'select a database':
				self.click_and_wait(s)
				break
		
		try:
			self.driver.switch_to_alert()
		except:
			print('no alert')

		try:
			popover = self.driver.find_element_by_css_selector('span.PopoverContainer')
			print('found popover ', popover)
		except:
			print('cant find popover!')

		# try:
		# 	kk = self.driver.find_elements_by_css_selector('h4.List-item-title')

		# 	print(len(kk))

		# 	for e in kk:
		# 		print(e.text)
		# except:
		# 	print('found no h4 listitems')

		for i_ in self.driver.find_elements_by_css_selector('h4.List-item-title'):
			if i_.text.strip().lower() == 'gcdm':
				print('found gcdm! clicking..')
				self.click_and_wait(i_)
				break

		# select_gcdm = self.driver.find_element_by_xpath('//*[@id="DatabasePicker"]/div/div[3]/div/a/h4')
		# self.click_and_wait(select_gcdm)
		actions = ActionChains(self.driver)

		textfield = self.driver.find_element_by_css_selector('div.ace_text-layer')

		actions.move_to_element(textfield)
		actions.click()
		# print('got textfield ', textfield)



		# try:
		# 	data_reference = self.driver.find_element_by_xpath('//span[contains(text(), "Data Reference")]')
		# except:
		# 	# note that this one is always there but may be invisible
		# 	data_reference = self.driver.find_element_by_css_selector('svg.Icon-reference')

		# self.click_and_wait(data_reference)

		# purple_button = self.driver.find_element_by_class_name('Button--purple')
		# self.click_and_wait(purple_button)

		# accounts = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3"]')

		# self.click_and_wait(accounts)

		# tables_in_samsung_accounts = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3/tables"]')

		# self.click_and_wait(tables_in_samsung_accounts)

		# customer_phones = self.driver.find_element_by_xpath('//a[@href="/reference/databases/3/tables/10"]')
		# self.click_and_wait(customer_phones)

		# see_this_table = self.driver.find_element_by_css_selector('span.mr1.flex-no-shrink')
		# self.click_and_wait(see_this_table, secs=8)

		# view_sql_button = self.driver.find_element_by_css_selector('svg.Icon-sql')
		# self.click_and_wait(view_sql_button)

		# self.driver.switch_to.active_element

		# convert_to_sql_button = self.driver.find_element_by_css_selector('a.Button--primary')
		# self.click_and_wait(convert_to_sql_button, secs=8)

		# textarea = self.driver.find_element_by_xpath('//*[@id="id_sql"]/textarea[@class="ace_text-input"]')

		# print(f'found {textarea} text area!')

		# self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)

		# print('scrolled into view..')

		# # textarea.clear()

		# textarea.send_keys(Keys.CONTROL + "a");
		# textarea.send_keys(Keys.DELETE)

		# time.sleep(4)

		#id_sql > textarea

		a_ = 'samsung_accounts.customer_phones'

		q = f"""
			SELECT [{a_}.age_bucket] AS age_group, [{a_}.carrier] AS carrier, [{a_}.category] AS category, 
					[{a_}.country] AS country, 
					[{a_}.first_seen] AS first_seen, 
					[{a_}.gender] AS gender,
					[{a_}.language] AS language, [{a_}.model] AS model, 
					[{a_}.number_of_devices] AS number_of_devices, 
					[{a_}.registration_date] AS registration_date,
					[{a_}.samsung_account_id] AS account_id, [{a_}.series] AS series
			FROM {a_} 
					WHERE (country = 'AUS') AND (age_bucket = '36-45') AND (DATE(first_seen) > DATE('2012-01-01')) AND (DATE(first_seen) < DATE('2012-02-01'))
			"""

		# textfield.send_keys(q)
		
		actions.send_keys(q)
		actions.perform()

		print('done action')

		time.sleep(6)

		print('trying to find get answer button..')
		get_answer_button = self.driver.find_element_by_css_selector('button.RunButton')
		self.click_and_wait(get_answer_button, secs=10)

		try:
			row_count = self.driver.find_element_by_css_selector('div.ShownRowCount').text.strip()
			print(row_count)
		except:
			print('cannot find row count!')

		download_full_results = self.driver.find_element_by_css_selector('svg.Icon-downarrow')
		self.click_and_wait(download_full_results)

		try:
			popover_body = self.driver.find_element_by_css_selector('div.PopoverBody.PopoverBody--withArrow')
		except:
			print('cant find popover body!')

		print('looking for the download as CSV button...')

		for b in self.driver.find_elements_by_css_selector('button.Button'):

			if b.text.strip().lower() == 'csv':
				print('found it! clicking..')
				self.click_and_wait(b)
				break

		print('resetting actions...')
		actions.reset_actions()
		print('done')
		
		try:
			ac = self.driver.find_element_by_css_selector('div.ace_content')
			print('found ac!')
			ac.clear()
		except:
			print('could not find and clear ac')

		try:
			ac = self.driver.find_element_by_css_selector('textarea.ace_text-input')
			# ac = self.driver.find_element_by_css_selector('div.ace_marker-layer')
			print('textarea!')
			print('trying to send keys to editor..')
			ac.send_keys(Keys.CONTROL + 'a')
			print('send ctrl + a')
			ac.send_keys(Keys.DELETE)
		except:
			print('could not find and clear ac editor')



		return self



if __name__ == '__main__':

	g = Grabber().sign_in().navigate_to_table()