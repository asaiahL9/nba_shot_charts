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
# used to create a print function that flushes the buffer
import functools     
flushprint = functools.partial(print, flush=True)       # create a print function that flushes the buffer immediately

player_id = '203999'
team_id = '1610612743'
game_id = '0022400350'
url = f'https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID={game_id}&PlayerID={player_id}&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID={team_id}&flag=3&sct=plot&section=game'
# irl = f'0https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID=0022400350&PlayerID=203999&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID=1610612743&flag=3&sct=plot&section=game'

# video_url = f'https://videos.nba.com/nba/pbp/media/{year}/{month}/{day}/{game_id}/303/f79cdfb8-c417-0a36-0f88-44a176b9a58a_1280x720.mp4'

print(url)
chrome_options = Options()
def get_data():
    #   print(url)
    # Set up the WebDriver (assuming you are using Chrome)
    #   print('here')
    # chrome_options.add_argument("--start-maximized")  # Start the browser maximized
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to Google's homepage
    driver.get(url)
    time.sleep(5)
    

  # Wait for the results to load and display the title
    driver.implicitly_wait(5)  # Wait up to 5 seconds for elements to appear
  # print(driver.title)
    render = driver.page_source
    with open("shot_chart.html", 'w', encoding='utf-8') as f:
        f.write(render)

def get_page():
    # chrome_options.add_argument("--headless")  # Run in headless mode
    # chrome_options.add_argument("--disable-gpu")  # Disable GPU (optional for headless)
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to Google's homepage
    driver.get(url)
    # time.sleep(5)
    wait = WebDriverWait(driver, 10)
    video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
    print("Page is loaded, and the <video> element is available.")
  # Wait for the results to load and display the title
    # driver.implicitly_wait(20)  # Wait up to 5 seconds for elements to appear
  # print(driver.title)
    render = driver.page_source
    with open("wait.html", 'w', encoding='utf-8') as f:
        f.write(render)
    print("page received")

def get_plays():
    with open('page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    shot_container = soup.find_all('tr', class_ = 'EventsTable_row__Gs8B9')
    # print(shot_container)
    with open('shot_container2.html', 'w', encoding='utf-8') as f:
        f.write(str(shot_container))
    for shot in shot_container:
        shot.find('a', href=True)['href']
    # print(str(shot_container))
    # # for shot in shot_container:
    # #     info = shot.find_all('tr', class_ = 'EventsTable_row__Gs8B9')

    #     # name = shot.find('h4')
    #     # print(name.text)
    #     # print(message.text, '\n')

def get_video():
    with open('page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    video_tag = soup.find('video')
    # response = requests.get(video_url, stream=True)
    # response.raise_for_status()
    video_url = video_tag.get('src')
    # video_src = source_tag['src']
    # print('video: ', source_tag)
    # Download the video using requests
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Save the video to a file
        video_filename = "video.mp4"
        with open(video_filename, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024):
                video_file.write(chunk)
        print(f"Video downloaded successfully as {video_filename}.")
    except Exception as e:
        print(f"Failed to download the video: {e}")
    else:
        print("No source URL found for the video element.")

if __name__ == "__main__":
    # get_plays()
    # get_page()
    get_video()