# This scrapes post content such as reactions, comments etc from Pages on Facebook and stores them in an Excel sheet in the same path as the Python file
# ChromeDriver is a pre-requisite for this
# Download ChromeDriver from https://chromedriver.chromium.org/ and place it in the same path as the Python file
from selenium import webdriver
import xlsxwriter
import time
import re
import datetime
#from random import randint
#from selenium.webdriver.common.keys import Keys

print "Start Time:", datetime.datetime.now()

# define values
# change these values as required
page_name = "Troll Assamese MEDIA" #the case-sensitive Facebook Page from which to extract post data
page_url = "https://www.facebook.com/Trollassammedia/" #URL of the group
user_name = "<your_user_name>" #username for Facebook login
password = "<your_password>" #password for Facebook login
pages_to_scrape = 3 #how far down the page should we scroll, maximum limit is around 150 pages

# format output Excel sheet
workbook = xlsxwriter.Workbook('FB_Data.xlsx') #Excel sheet name, change this if you want
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, 'DATE')
worksheet.write(0, 1, 'POST')
worksheet.write(0, 2, 'REACTIONS')
worksheet.write(0, 3, 'COMMENTS')
worksheet.write(0, 4, 'SHARES')

# define starting row in excel
row = 1
check = 1
# default time to wait for page actions so that the page loads fully before we proceed, change this if required
time_to_sleep = 5
time.sleep(time_to_sleep)
posts = [] # define list for posts

# function to extract numbers from string
def extract_number(inp_value):
    try:
        # check if the value is expressed in the form 9K
        check_for_k = re.search(r'[\d+][K]', inp_value)

        # keep only numbers and decimals
        only_num = re.compile(r'[^\d.]+')
        likes = only_num.sub('', inp_value)

        #if value had K in it, multiply by 1000
        if check_for_k:
            likes = int(float(likes) * 1000)
    except:
        likes = "99999"
        pass
    return likes

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

# disable notifications on Chrome so that these don't interfere with the scraping process
# disable loading of images to make the page loads faster
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

# start scraping
# scroll as many pages as indicated
while check <= pages_to_scrape:
    print "Page:", check, " loaded"
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
    time.sleep(time_to_sleep)  # Sleep here, let page scroll load
    check += 1

# find posts
posts = driver.find_elements_by_xpath("//div[@class='_5pcr userContentWrapper']")
for post in posts:  # loop through each post element
    post_content = post.find_element_by_xpath(".//div[1]")
    try:
        # get first line of post
        first_line = post_content.text.splitlines()[0]
    except:
        first_line = "Could not extract first line"
        print "Error: ", first_line
        pass
    # process only if it is a post by the defined group
    # added this check since the code picks up posts from other groups added as comments
    if page_name in first_line:
        print "Post Content: ", post_content.text
        second_line = post_content.text.splitlines()[1]  # extract second line which has the post time
        second_line = re.sub('[^A-Za-z0-9]+', '', second_line)  # remove all special chars from second line
        print "Second Line:", second_line
        post_date = extract_date(second_line) # get the date of the post
        print "Extracted Post Date:", post_date
        worksheet.write(row, 0, post_date)
        worksheet.write(row, 1, post_content.text)
        try:
            reactions = post.find_element_by_xpath(".//div[2]//*[@class='_3dlh _3dli']") # get reactions
            reactions = str(reactions.text)
            print "Reactions: ", reactions
            reactions = extract_number(reactions)
            worksheet.write(row, 2, reactions)
        except:
            pass
        try:
            comments = post.find_element_by_xpath(".//div[2]//a[@class='_3hg- _42ft']") # get comments
            print "Comments: ", comments.text
            comments = extract_number(comments.text)
            worksheet.write(row, 3, comments)
        except:
            pass
        try:
            shares = post.find_element_by_xpath(".//div[2]//a[@class='_3rwx _42ft']") # get shares
            print "Shares: ", shares.text
            shares = extract_number(shares.text)
            worksheet.write(row, 4, shares)
        except:
            pass
        print"++++++++++++++++++++"
        row += 1


driver.quit()
workbook.close()
print "End Time:", datetime.datetime.now()