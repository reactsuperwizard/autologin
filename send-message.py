 

#Importing packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
import datetime

import pymysql
import re

# get member name by member_id
def get_member_name(member_id):
	#sql = "SELECT name FROM f_members WHERE member_id = '" + str(member_id) + "'"
	sql = "SELECT name FROM users WHERE id = '" + str(member_id) + "'"
	mycursor.execute(sql)
	myresult = mycursor.fetchall()
	if len(myresult) == 0 :
		return None

	name_list = myresult[0]
	name = name_list[0]
	return name

# send message in member_name
def send_message(name, message, message_id):
	user_list = driver.find_elements_by_css_selector("fl-bit.MainRow")
	
	count_user_list = len(user_list)
	print("########## You can see user's list ##########")
	print("count user = " + str(count_user_list))
	back_username = ""	

	for user_item in user_list:
		tmp_data = user_item.find_elements_by_css_selector("img.UserAvatar-img")
		if (tmp_data != []):
			username = tmp_data[0].get_attribute("title")
		else:
			tmp_data = user_item.find_elements_by_css_selector("fl-text.Title")
			if (tmp_data != []):
				username = tmp_data[0].text
			else:
				continue
				
		print ("username : " + username + "," + "reciever:" + name)
		if (name == username):
			user_item.click()
			time.sleep(2)
			textarea = driver.find_elements_by_tag_name("textarea")			
			textarea[0].send_keys(message)
			textarea[0].send_keys('\ue007')
			print(textarea)			
			sql = "UPDATE f_messages SET sent = 1 WHERE id = '" + str(message_id) + "'"
			mycursor.execute(sql)
			mydb.commit()
			


# parse IDs and messages in https://www.freelancer.com/messages
def process_function():
	print(driver.current_url)	
	while(1):
		time.sleep(1)
		print ("now while")
		sql = "SELECT * FROM f_messages WHERE sent = 0"		
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		# print(myresult);		
		for x in myresult:
			# print(x)
			member_name = get_member_name(x[2])			
			if member_name == None :
				continue
			message = x[3]
			message_id = x[0]
			send_message(member_name, message, message_id);		
		mydb.commit()



#################################
#	process main()		#
#################################

# connect mysql db and tables
# mydb = mysql.connector.connect(
# 	host = "18.236.151.181",
# 	user = "star",
# 	passwd = "starstars",
# 	database = "ssystem"
# )
pymysql.install_as_MySQLdb()
import MySQLdb
mydb = MySQLdb.connect("localhost" , "root" , "", "ssystem")


mycursor = mydb.cursor()
mycursor.execute("SHOW TABLES")

member_flage = 0
message_flage = 0

for x in mycursor:
	print(x)
	if (re.search(r'users', str(x))):
		member_flage = 1
	if (re.search(r'f_messages', str(x))):
		message_flage = 1

if (member_flage == 0):
	print ("member tables is false.")
else:
	print ("member table is true.")
if (message_flage == 0):
	print ("message table is false.")
else:
	print ("message table is true.")


driver_options = webdriver.ChromeOptions()

# get username and password
file = open('freelancer-user.env', "r")
read = file.read()

freelancer_username = ""
freelancer_password = ""
proxy_ip = ""
proxy_port = ""
platform_id = ""

for line in read.splitlines():
	tmp_item =  line.split('=',1)
	if (tmp_item == []):
		continue
	else:
		if ('F_USERNAME' in tmp_item[0]):
			print ("username = " + tmp_item[1])
			freelancer_username = tmp_item[1]
		if ('F_PASSWORD' in tmp_item[0]):
			#print ("password = " + tmp_item[1])
			freelancer_password = tmp_item[1]
		if ('PROXY_IP' in tmp_item[0]):
			print ("proxy ip = " + tmp_item[1])
			proxy_ip = tmp_item[1]
		if ('PROXY_PORT' in tmp_item[0]):
			print ("proxy port = " + tmp_item[1])
			proxy_port = tmp_item[1]
		if ('PLATFORM_ID' in tmp_item[0]):
			print ("platform id = " + tmp_item[1])
			platform_id = tmp_item[1]

# call freelancer login page
# driver_options.add_argument('--proxy-server=%s:%s' %(proxy_ip, proxy_port))
driver_options.add_argument('--headless')
driver_options.add_argument('--ignore-certificate-errors')
driver_options.add_argument("--start-maximized");
driver_options.add_argument("--disable-notifications")
driver_options.add_argument("--disable-gpu")
driver_options.add_argument("--disable-popup-blocking")
driver_options.add_argument("--disable-infobars")
driver_options.add_argument("--disable-extensions")
driver_options.add_argument('--no-sandbox')
driver_options.add_argument("--no-zygote")
driver_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options = driver_options)


driver.get("https://www.freelancer.com/login")
# auto login in login page
driver.find_element_by_id("username").send_keys(freelancer_username)
driver.find_element_by_id ("password").send_keys(freelancer_password)
time.sleep(3)
driver.find_element_by_id ("password").send_keys("\ue007")
time.sleep(5)

# call freelancer messages page
driver.get("https://www.freelancer.com/messages")
time.sleep(1)
process_function()

