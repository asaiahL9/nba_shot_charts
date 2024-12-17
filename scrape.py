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
from pathlib import Path
import pandas as pd
# used to create a print function that flushes the buffer
import functools     
flushprint = functools.partial(print, flush=True)       # create a print function that flushes the buffer immediately
fields = ["PLAYER",	"PLAY TYPE", "MADE", "SHOT TYPE", "BOXSCORE", "VTM", "HTM",	"Game Date", "PERIOD", "TIME REMAINING", "SHOT DISTANCE (FT)", "TEAM"]
player_id = '203999'
team_id = '1610612743'
game_id = '0022400350'
url = f'https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID={game_id}&PlayerID={player_id}&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID={team_id}&flag=3&sct=plot&section=game'
# irl = f'0https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID=0022400350&PlayerID=203999&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID=1610612743&flag=3&sct=plot&section=game'

# video_url = f'https://videos.nba.com/nba/pbp/media/{year}/{month}/{day}/{game_id}/303/f79cdfb8-c417-0a36-0f88-44a176b9a58a_1280x720.mp4'

print(url)
chrome_options = Options()

# def open_driver():
#     #   print(url)
#     # Set up the WebDriver (assuming you are using Chrome)
#     #   print('here')
#     # chrome_options.add_argument("--start-maximized")  # Start the browser maximized
#     driver = webdriver.Chrome(options=chrome_options)

#     # Navigate to Google's homepage
#     driver.get(url)
#     time.sleep(5)
    

#   # Wait for the results to load and display the title
#     driver.implicitly_wait(5)  # Wait up to 5 seconds for elements to appear
#   # print(driver.title)
#     render = driver.page_source
#     with open("shot_chart.html", 'w', encoding='utf-8') as f:
#         f.write(render)

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
    time.sleep(2)
    video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
    print("Page is loaded, and the <video> element is available.")
  # Wait for the results to load and display the title
    # driver.implicitly_wait(20)  # Wait up to 5 seconds for elements to appear
  # print(driver.title)
    render = driver.page_source
    # soup = BeautifulSoup(render, 'html_parser')
    shots, play_container = get_shots(render)
    for play in play_container:
        try:
            # Find the <tr> element using its class and attribute
            tr_element = driver.find_element(By.XPATH, '//tr[@class="EventsTable_row__Gs8B9" and @data-is-playing="true"]')

            # Scroll to the element if it's not visible
            # driver.execute_script("arguments[0].scrollIntoView(true);", tr_element)

            # Click the element
            tr_element.click()

            print("Element clicked successfully!")

        except Exception as e:
            print(f"Error: {e}")
        # time.sleep(1)
        video_file = get_video(shots, play_container, render)
        for shot in shots:
            shot['video_file'] = video_file
            print("video_file", video_file)
        plays_df = shots_to_df(shots, video_file)

    with open("page.html", 'w', encoding='utf-8') as f:
        f.write(render)
    print(plays_df)
    # print("page received")

def get_shots(page):
    shots = []
    # with open('page.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    # page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    play_container = soup.find_all('tr', class_ = 'EventsTable_row__Gs8B9')
    # print(shot_container)
    with open('shot_container2.html', 'w', encoding='utf-8') as f:
        f.write(str(play_container))
    
    for play in play_container:
        play_attr = play.find_all('td', class_='Crom_text__NpR1_')
        # print(play_attr)
        link = play.find('a', href=True)
        link = link.get('href')
        play_text = ', '.join(td.get_text(strip=True) for td in play_attr)
        # print(play_text)
        play_details = [td.get_text(strip=True) for td in play_attr]
        # print(play_details)
        entry = dict(zip(fields, play_details))
        shots.append(entry)
    print(shots)
    # df = pd.DataFrame(shots)
    # df.to_csv('shots.csv', index=False)
    return shots, play_container

def shots_to_df(shots, video_file):
    # shots, play_container = get_shots()
    # video = get_video(shots, play_container)
    df = pd.DataFrame(shots)
    df['VIDEO_FILE'] = video_file
    df.to_csv('shots2.csv')
    return df

def get_video(shots, play_container, page):
    video_filename = ''
    # get_page()
    # with open('page.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    # page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    # for play in play_container:
    video_tag = soup.find('video')
    # response = requests.get(video_url, stream=True)
    # response.raise_for_status()
    video_url = video_tag.get('src')
    print("video_url", video_url)
    # video_src = source_tag['src']
    # print('video: ', source_tag)
    # Download the video using requests
    if video_url:
        print("Video URL:", video_url)
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()

            # Save the video to a file
            # video_filename = "video.mp4"
            video_filename = "".join(str(value) for value in shots.values()) + ".mp4"
            with open(video_filename, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024):
                    video_file.write(chunk)
            print()
        except Exception as e:
            print()
    else:
        print("No source URL found for the video element.")
        video_filename = "default_video.mp4"
    return video_filename

# def manage_files():


if __name__ == "__main__":
    get_page()
    # get_shots()
    # get_page()
    # get_video()
    # shots_to_df()






# def get_video():
#     with open('page.html', 'r', encoding='utf-8') as f:
#         html_content = f.read()
#     page = html_content
#     soup = BeautifulSoup(page, 'html.parser') # #parsing html content
#     video_tag = soup.find('video')
#     # response = requests.get(video_url, stream=True)
#     # response.raise_for_status()
#     video_url = video_tag.get('src')
#     # video_src = source_tag['src']
#     # print('video: ', source_tag)
#     # Download the video using requests
#     if video_url:
#         print("Video URL:", video_url)
#         try:
#             response = requests.get(video_url, stream=True)
#             response.raise_for_status()

#             # Save the video to a file
#             video_filename = "video.mp4"
#             with open(video_filename, "wb") as video_file:
#                 for chunk in response.iter_content(chunk_size=1024):
#                     video_file.write(chunk)
#             print(f"Video downloaded successfully as {video_filename}.")
#         except Exception as e:
#             print(f"Failed to download the video: {e}")
#     else:
#         print("No source URL found for the video element.")
#     return

# def get_plays():
#     shots = []
#     with open('page.html', 'r', encoding='utf-8') as f:
#         html_content = f.read()
#     page = html_content
#     soup = BeautifulSoup(page, 'html.parser') # #parsing html content
#     play_container = soup.find_all('tr', class_ = 'EventsTable_row__Gs8B9')
#     # print(shot_container)
#     with open('shot_container2.html', 'w', encoding='utf-8') as f:
#         f.write(str(play_container))
    
#     for play in play_container:
#         play_attr = play.find_all('td', class_='Crom_text__NpR1_')
#         # print(play_attr)
#         link = play.find('a', href=True)
#         link = link.get('href')
#         play_text = ', '.join(td.get_text(strip=True) for td in play_attr)
#         # print(play_text)
#         play_details = [td.get_text(strip=True) for td in play_attr]
#         entry = dict(zip(fields, play_details))
#         shots.append(entry)
#     # Print the list
#         # print(play_details)
#         # for attr in play_attr:
#         # #     print(attr.text)
#             # link = play.find('a', href=True)
#             # link = link.get('href')
#         #     print(play_attr[0].text, play_attr[1].text,play_attr[2].text, link)
#         # print(name, link, shot_type)
#     # print(str(shot_container))
#     # # for shot in shot_container:
#     # #     info = shot.find_all('tr', class_ = 'EventsTable_row__Gs8B9')

#     #     # name = shot.find('h4')
#     #     # print(name.text)
#     #     # print(message.text, '\n')