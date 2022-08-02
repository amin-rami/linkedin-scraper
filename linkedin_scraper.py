import time
from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3

base_address = "https://www.linkedin.com"

#choosing proper options for webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=C:\\selenium") 
chrome_options.add_argument("--incognito")
#WARNING: please install chrome version 104 with it's
#corresponding webdriver. otherwise program won't work!
chrome_options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.maximize_window()
browser.set_window_size(1000, 1000)

#creating a list to save the log data
log_data = []

#going to login page
browser.get('https://www.linkedin.com/login')

#username and password of the account whose connections 
#we want to scrape. you can change the user/pass to acces
#another account
username = 'email@example.com'
password = '123456789'

#finding and filling out the username/password fields
elementID = browser.find_element(value = 'username')
elementID.send_keys(username)
elementID = browser.find_element(value = 'password')
elementID.send_keys(password)
elementID.submit()

#getting log info
time.sleep(4)
log_data.extend(browser.get_log('browser'))

#going to owner's main page to extract his/her information
browser.get("https://www.linkedin.com/feed/")
time.sleep(4)
log_data.extend(browser.get_log('browser'))
src = BeautifulSoup(browser.page_source, 'lxml')

#extracting owner's name
my_name = src.find('div', class_ = 't-16 t-black t-bold')
my_name = str(my_name.text).strip()
#extracting owner's job title
my_occupation = src.find('p', class_ = 'identity-headline t-12 t-black--light t-normal mt1')
my_occupation = str(my_occupation.text).strip()
my_time = ""
#extracting owner's page address
my_address = src.find('div', class_ = "feed-identity-module__actor-meta break-words")
my_address = base_address + str(my_address.find('a')['href'])

#going to owner's connection page to extract information
# of his/her connections
browser.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")

#scrolling through all connections
initialScroll = 0
finalScroll = 1000
old_height = 0
new_height = 0
time.sleep(3)
flag = False
while True:
    s = "window.scrollTo(" +str(initialScroll)+","+str(finalScroll)+")"
    time.sleep(4)
    browser.execute_script(s)
    initialScroll = finalScroll
    
    old_height = new_height
    new_height = browser.execute_script("return document.body.scrollHeight")
    
    if old_height == new_height:
        if flag == False:
            button = browser.maximize_window()
            flag = True
        else:
            break
    
    finalScroll += 30000
  
    
#getting log info
time.sleep(4)
log_data.extend(browser.get_log('browser'))

#getting the source code of the page
src = BeautifulSoup(browser.page_source, 'lxml')

#extracting names of the connections
connection_pane = src.find('div', class_ = 'scaffold-finite-scroll__content')
name = connection_pane.find_all('span', class_ = 'mn-connection-card__name t-16 t-black t-bold')
#extracting job titles of the connections
occupation = connection_pane.find_all('span', class_ = 'mn-connection-card__occupation t-14 t-black--light t-normal')
#extracting connection time of the connections
connection_time = connection_pane.find_all('time', class_ = 'time-badge t-12 t-black--light t-normal')
#extracting page address of the connections
address = src.find_all('div', class_ = "mn-connection-card__details")

browser.close()

#trimming and beautifying the extracted information    
len_ = len(name)
for i in range(len_):
    name[i] = str(name[i].text).strip()
    occupation[i] = str(occupation[i].text).strip()
    connection_time[i] = str(connection_time[i].text).strip()
    connection_time[i] = connection_time[i].replace('\n', " ")
    connection_time[i] = " ".join(connection_time[i].split())
    address[i] = base_address + str(address[i].find('a')['href'])

#adding the owner's iformation to connection's information
name.insert(0, my_name)
occupation.insert(0, my_occupation)
connection_time.insert(0, my_time)
address.insert(0, my_address)
len_ = len_ + 1

#saving all the information in a sql database
conn = sqlite3.connect('linkedin_info.db')
crs = conn.cursor()

#creating a table
crs.execute('''CREATE TABLE linkedin(
    Row INTEGER PRIMARY KEY,
    Full_Name TEXT,
    Job_Title TEXT,
    Connection_Time TEXT,
    Page_Address TEXT
    )''')

#inserting the gathered data into the table
for i in range(len_):
    crs.execute("INSERT INTO linkedin VALUES (?, ?, ?, ?, ?)", (i+1, name[i], occupation[i], connection_time[i], address[i]))
    conn.commit()
conn.close()

#saving the log data in a .log file
with open ('linkedin.log', 'w') as file:
    for item in log_data:
        file.write(str(item)+"\n")
        
        
        
