# This script will take a Facebook Page and a date as an input
# and display posts on the Page from that date
# this is pretty buggy at this point
from selenium import webdriver
import xlsxwriter
import time
import re
import datetime

print "Start Time:", datetime.datetime.now()

# define values
page_name = "<name_of_the_Page>" #the case-sensitive Facebook Page from which to extract post data
page_url = "https://www.facebook.com/XXXXXX/" #URL of the Page
user_name = "gumpsujoy@gmail.com" #username for Facebook login
password = "iI_am_Mama@1983k" #password for Facebook login
# enter the date in this format, since the script scrolls through the Page looking for this date,
# this might not works for dates too far back in the past
open_page_for_date = '2019-08-25'
input_date = datetime.datetime.strptime(open_page_for_date,'%Y-%m-%d')
check = 1
# default time to wait for page actions
time_to_sleep = 5


# function to extract dates from string
def extract_date(text):
    extracted_date = ""
    # check for today's date
    if "sec" in text or "min" in text or "hr" in text:
        extracted_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # check for yesterday's date
    elif "Yesterday" in text:
        extracted_date = (datetime.datetime.now() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    # check for current year's date
    elif "at" in text:
        regex = re.compile('(?P<before_at>.+)at')
        extracted_date = regex.search(text).group('before_at')
        try:
            extracted_date = datetime.datetime.strptime(extracted_date, '%d%B')
            extracted_date = extracted_date.strftime(datetime.datetime.now().strftime("%Y") + "-%m-%d")
        except ValueError:
            pass
    # skip if none of these
    else:
        pass
    # check for date in dd Mon YYYY format
    if not extracted_date:
        try:
            extracted_date = datetime.datetime.strptime(text, '%d%B%Y')
            extracted_date = extracted_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    # check for date in Mon YYYY format
    if not extracted_date:
        try:
            extracted_date = datetime.datetime.strptime(text, '%d%B')
            extracted_date = extracted_date.strftime(datetime.datetime.now().strftime("%Y") + "-%m-%d")
        except ValueError:
            pass
    return extracted_date

# disable notifications
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
prefs1 = {"profile.managed_default_content_settings.images": 2}
prefs.update(prefs1)
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(chrome_options=chrome_options)


# login
driver.get("https:www.facebook.com")
driver.find_element_by_id("email").send_keys(user_name)
driver.find_element_by_id("pass").send_keys(password)
driver.find_element_by_id("loginbutton").click()
# open page
time.sleep(time_to_sleep)
driver.get(page_url)
time.sleep(time_to_sleep) #sleep after initial page load

# scroll as many pages as required until we get to a page
# with a post from the required date
while True:
    print "Page:", check, " loaded"
    current_posts = driver.find_elements_by_xpath("//div[@class='_5pcr userContentWrapper']") #get all posts loaded till now
    post_content =  current_posts[-1].find_element_by_xpath(".//div[1]") #get last post in the list
    #print "Content of last post in the list: ", post_content.text
    second_line = post_content.text.splitlines()[1]  # extract second line which has the post time
    second_line = re.sub('[^A-Za-z0-9]+', '', second_line)  # remove all special chars from second line
    post_date = extract_date(second_line)  # get the date of the post
    print "Date of last post on the page:", post_date
    # if the post is from the required date, break loop and display page
    if datetime.datetime.strptime(post_date,'%Y-%m-%d').date() == input_date.date():
        break
    # continue loading more pages
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
    time.sleep(time_to_sleep)  # Sleep here, let page scroll load
    check += 1

#driver.quit()
print "End Time:", datetime.datetime.now()