# In[1]
import pickle
import re
from random import randint

import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
import time
from bs4 import BeautifulSoup as bs
from DocumentRetrievalModel import DocumentRetrievalModel as DRM
from ProcessedQuestion import ProcessedQuestion as PQ
import re
import sys
with open('title.pickle','rb') as file:
	TITLES = pickle.load(file)
greetPattern = re.compile("^\ *((hi+)|((good\ )?morning|evening|afternoon)|(he((llo)|y+)))\ *$",re.IGNORECASE)

chrome_options = Options()
chrome_options.add_argument('user-data-dir=user_data')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("start-maximized")

# In[2]
def extract_email(line):
	try:
		match = re.search(r'[\w\.-]+@[\w\.-]+', line)
		return match.group(0)
	except:
		return ''
class Setup:

	def __init__(self):
		try:
			with open('data.pickle','rb') as file:
				self.post_data = pickle.load(file)
		except:
			self.post_data = []
		with open('logininfo.txt','r') as file:
			lines = file.readlines()
			self.__user = lines[0]
			self.__passwd = lines[1]
			self.group_links = lines[2:]
		self.driver = Chrome(options=chrome_options)
		self.driver.set_window_size(1200, 700)
		self.driver.get("https://www.facebook.com")
		if self.check_login_needed():
			self.login()

		self.srchStr = "https://www.facebook.com/search/people/?q={}&epa=SERP_TAB"

	def check_login_needed(self)->bool:
		pass
	def login(self):
		user, passwd = self.__user,self.__passwd
		self.driver.find_element_by_css_selector('[name="email"]').clear()
		self.driver.find_element_by_css_selector('[name="email"]').send_keys(user)
		self.driver.find_element_by_css_selector('[name="pass"]').clear()
		self.driver.find_element_by_css_selector('[name="pass"]').send_keys(passwd)
		self.driver.find_element_by_xpath('//*[@type="submit"]').click()
		time.sleep(1)


	def action(self):
		pass

	def crawl_group(self,link):
		# test link 	https://www.facebook.com/groups/palmayachtcrew/
		self.driver.get(link)
		self.group_name = self.driver.find_element_by_css_selector('h1#seo_h1_tag').text
		# Get All Posts.
		for i in range(100):
			self.driver.execute_script('window.scrollBy(0,2500);')
			time.sleep(10)
		allposts = self.driver.find_elements_by_css_selector('[role="article"][id]')
		for i in allposts:
			self.crawl_post(i)
	def crawl_post(self,element):
		try:
			text = bs(element.find_element_by_css_selector('[data-testid="post_message"]').get_attribute('innerHTML')).text
			email = extract_email(text)
			group_name = self.group_name
			title,experience,size = get_features(text)
			if text!='':
				self.post_data.append([group_name,text,email,title,experience,size])
			return True
		except:
			return False


	def __del__(self):
		self.driver.close()
		with open('data.pickle','wb') as wb:
			pickle.dump(self.post_data,wb)

def get_features(datasetFile:str):
	paragraphs = []
	for para in datasetFile.split('\n'):
		if (len(para.strip()) > 0):
			paragraphs.append(para.strip())

	# Processing Paragraphs
	drm = DRM(paragraphs, True, True)

	questions  = ['experience','size']
	answers = []
	for i in TITLES:
		for j in TITLES[i]:
			userQuery = j
			pq = PQ(userQuery, True, False, True)
			response = drm.query(pq)
			if response != ' ': break
		else:
			continue
		break
	else:
		i = ''
	answers.append(i)

	for i in questions:
		userQuery = i
		pq = PQ(userQuery, True, False, True)

		# Get Response From Bot
		response = drm.query(pq)
		answers.append(response)
	return answers

# In[3]


self = Setup()


self.crawl_group("https://www.facebook.com/groups/palmayachtcrew/")
#%%
import mysqldata
connection = mysqldata.con('')

df = pd.DataFrame(self.post_data)
df.to_excel('data.xlsx',index=False)
df.to_json('data.json')
for data in self.post_data:
	connection.addData(data=data)

#%%
# End Method
self.__del__()

#%%
