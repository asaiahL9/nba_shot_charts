import requests
from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm
import re
import os
import time
from pathlib import Path
from rich import print
from selenium import webdriver                          # used to render the web page
# from seleniumwire import webdriver                      
from selenium.webdriver.chrome.service import Service   # Service is only needed for ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path
import pandas as pd
# used to create a print function that flushes the buffer
import functools     
# fields ,SVG,PLAYER,PLAY TYPE,MADE,SHOT TYPE,BOXSCORE,VTM,HTM,Game Date,PERIOD,TIME REMAINING,SHOT DISTANCE (FT),TEAM
# 1,,Nikola Jokić,Driving Floating Jump Shot,✖Missed Shot,2PT Field Goal, DEN @ ATL, DEN , ATL ,"Sunday, December 8",1,08:10,2,Denver Nuggets

class Play:
    # Constructor to initialize attributes
    def __init__(self, player, play_type, made, shot_type, boxscore, vtm, htm, date, period, time_remaining, shot_distance, team, video_id, video_url):
        self.player = player  # Attribute
        self.age = age    # Attribute

    # Method to display person's details
    def introduce(self):
        print(f"Hi, my name is {self.name} and I am {self.age} years old.")

    # Method to update the age
    def birthday(self):
        self.age += 1
        print(f"Happy Birthday, {self.name}! You are now {self.age}.")

def multiple_replace(text, repl_dict):
    pattern = re.compile("|".join(map(re.escape, repl_dict.keys())))
    return pattern.sub(lambda match: repl_dict[match.group(0)], text)

# Function to move the cursor to a target element
def move_cursor_to_element(driver, element):
    # Get the element's position and size
    location = element.location
    size = element.size
    center_x = location['x'] + size['width'] / 2
    center_y = location['y'] + size['height'] / 2

    # Ensure the cursor script is executed (if not already)
    driver.execute_script(cursor_script)

    # Move the cursor to the element position
    driver.execute_script(f"moveCursor({center_x}, {center_y});")
    print(f"Cursor moved to: {center_x}, {center_y}")

def get_page():
    # chrome_options.add_argument("--headless")  # Run in headless mode
    # chrome_options.add_argument("--disable-gpu")  # Disable GPU (optional for headless)
    driver = webdriver.Chrome(options=chrome_options)
    # Create an ActionChains object
    actions = ActionChains(driver)

    # Navigate to Google's homepage
    driver.get(url)
    # driver.execute_script(cursor_script)
    # time.sleep(5)
    wait = WebDriverWait(driver, 10)
    # time.sleep(2)
    video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
    # cookie_banner = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
    time.sleep(3)
    hide_banners(driver)
    
    # Inject JavaScript to pause the video
    driver.execute_script("arguments[0].pause();", video_element)
    print("Video paused successfully!")
    print("Page is loaded, and the <video> element is available.")
    render = driver.page_source
    # soup = BeautifulSoup(render, 'html_parser')
    plays, play_container = get_plays(driver, render)
    welements = get_webelements(driver)
    videos = []
    # Iterate through each row to extract its position
    with open("locations.txt", 'w') as f:
        for index, play in enumerate(plays):
            # location = play.location
            # size = play.size
            
            # f.write(str(location) + " | " + str(size) + '\n')
            # try:
            #     # handle_popups(driver)
            #     # hide_banners(driver)
            #     # close_elements = driver.find_elements(By.CSS_SELECTOR, "svg.bx-close-xsvg")
                try:
                    # Check for the presence of the element
                    close_element = driver.find_element(By.CSS_SELECTOR, "svg.bx-close-xsvg, button.bx-close-inside")
                    if close_element:
                        print("Close button found. Clicking the element...")
                        actions.move_to_element(close_element).click().perform()
                    time.sleep(1)
                    # close_element.click()  # Click the element
                except NoSuchElementException:
                    print("Element not found.")
                actions.click(welements[index]).perform()
                print('element clicked')
                time.sleep(2)  # Add delay if needed for page actions to complete
                render = driver.page_source
                video_file = get_video(index, plays, play_container, render, videos)
                plays[index]['VIDEO_FILE'] = video_file
                plays_df = plays_to_df(plays, video_file)
                # print(plays_df)
            # except Exception as e:
            #     print(f"Error: {e}")
            # print(f"Row {index}: Location -> {location}, Size -> {size}")
    plays_df = plays_df.drop(columns=['VIDEO_FILE'])
    plays_df.to_csv('plays.csv')

    with open("page.html", 'w', encoding='utf-8') as f:
        f.write(render)
    # print(plays_df)
    # print("page received")

def handle_popups(driver):
    try:
        alert = Alert(driver)
        alert.dismiss()  # or alert.accept()
    except:
        print("No alert found")

def get_webelements(driver):
    webelements = []
    # driver.find_element(By.XPATH, '//tr[@class="EventsTable_row__Gs8B9"]')
    elements = driver.find_elements(By.CLASS_NAME, "EventsTable_row__Gs8B9")
    for index, element in enumerate(elements, start=1):
        location = element.location
        size = element.size
        webelements.append(element)
        # print(f"Row {index}: Location -> {location}, Size -> {size}")
    # print(*webelements)
    # for i in webelements:
    #     print(i)
    return webelements
    # Loop through elements and click them 

def get_plays(driver, page):
    plays = []
    # with open('page.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    # page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    play_container = soup.find_all('tr', class_ = 'EventsTable_row__Gs8B9')
    # print(play_container)
    with open('shot_container2.html', 'w', encoding='utf-8') as f:
        f.write(str(play_container))
    
    for play in play_container:
        play_attr = play.find_all('td')
        # play_details = [td.get_text().strip() for td in play_attr if not td.find('svg') and td.get_text().strip()]
        # print(play_attr)
        link = play.find('a', href=True)
        link = link.get('href')
        # play_text = ', '.join(td.get_text().strip() for td in play_attr)
        # print(play_text)
        play_details = [td.get_text() for td in play_attr]
        print("details: ", play_details)
        entry = dict(zip(fields, play_details))
        plays.append(entry)
    # print(plays)
    df = pd.DataFrame(plays)
    df.to_csv('plays.csv', index=False)
    return plays, play_container