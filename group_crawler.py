#!/usr/bin/python3
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
import mysqldata


with open('title.pickle','rb') as file:
	TITLES = pickle.load(file)
greetPattern = re.compile("^\ *((hi+)|((good\ )?morning|evening|afternoon)|(he((llo)|y+)))\ *$",re.IGNORECASE)

chrome_options = Options()
# chrome_options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument('user-data-dir=user_data')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('headless')
# In[2]
def extract_email(line):
	try:
		match = re.search(r'[\w\.-]+@[\w\.-]+', line)
		return match.group(0)
	except:
		return ''
class Setup:

	def __init__(self,posts):
		self.post_data = []
		with open('logininfo.txt','r') as file:
			lines = file.readlines()
			self.__user = lines[0]
			self.__passwd = lines[1]
			self.group_links = lines[2:]
		self.driver = Chrome(options=chrome_options,)
		self.driver.set_window_size(1200, 700)
		self.driver.get("https://www.facebook.com")
		try:
			self.login()
		except Exception as e:
			print("ALready Logged in")
			pass
		self.posts = posts
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

	def add_done(self):
		pass
	def action(self):
		pass

	def crawl_group(self,link):
		# test link 	https://www.facebook.com/groups/palmayachtcrew/
		self.driver.get(link+'?sorting_setting=CHRONOLOGICAL')
		self.group_name = self.driver.find_element_by_css_selector('h1#seo_h1_tag').text
		# Get All Posts.
		print("Scrolling")
		for i in range(randint(5,8)):
			self.driver.execute_script('window.scrollBy(0,3500);')
			print("scrolled", i, end='\r', flush=True)
			time.sleep(randint(5,20))
		print("Getting data From post")
		allposts = self.driver.find_elements_by_css_selector('[data-testid="newsFeedStream"] [role="article"][id]')
		for i in allposts:
			self.crawl_post(i)

	def crawl_post(self,element):
		try:
			text = bs(element.find_element_by_css_selector('[data-testid="post_message"]').get_attribute('innerHTML')).text
			if text in self.posts: return False
			email = extract_email(text)
			if email == '': return False
			group_name = self.group_name
			title, experience, size = get_features(text)

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


connection = mysqldata.con('')
connection.createcon()
cur = connection.con.cursor()
cur.execute('select message from job_detail_fb_demo')
x = cur.fetchall()
x = [i[0] for i in x]
self = Setup(x)
groups = connection.get_groups()
#%%
for link in groups:

	self.crawl_group(link)
	print("Get data Successful from\t", link)
#%%

df = pd.DataFrame(self.post_data)
df.to_excel('data.xlsx',index=False)
print("File Saved to Data.xlsx")
df.to_json('data.json')
for data in self.post_data:
	connection.addData(data=data)

#%%

#%%
