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

flushprint = functools.partial(print, flush=True)       # create a print function that flushes the buffer immediately
fields = ["SVG", "PLAYER",	"PLAY TYPE", "MADE", "SHOT TYPE", "BOXSCORE", "VTM", "HTM",	"Game Date", "PERIOD", "TIME REMAINING", "SHOT DISTANCE (FT)", "TEAM"]
player_id = '203999'
team_id = '1610612743'
game_id = '0022400350'
url = f'https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID={game_id}&PlayerID={player_id}&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID={team_id}&flag=3&sct=plot&section=game'
# irl = f'0https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID=0022400350&PlayerID=203999&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID=1610612743&flag=3&sct=plot&section=game'

# video_url = f'https://videos.nba.com/nba/pbp/media/{year}/{month}/{day}/{game_id}/303/f79cdfb8-c417-0a36-0f88-44a176b9a58a_1280x720.mp4'

# print(url)
# Set up Chrome options
# chrome_options = Options()
# Uncomment for headless mode
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")  # Optional for headless

# Inject a custom cursor into the webpage
cursor_script = """
    if (!document.getElementById('custom-cursor')) {
        // Create a custom cursor element
        var cursor = document.createElement('div');
        cursor.id = 'custom-cursor';
        cursor.style.position = 'absolute';
        cursor.style.width = '10px';
        cursor.style.height = '10px';
        cursor.style.backgroundColor = 'red';
        cursor.style.borderRadius = '50%';
        cursor.style.zIndex = '10000';
        cursor.style.pointerEvents = 'none';
        document.body.appendChild(cursor);

        // Define the moveCursor function
        window.moveCursor = function(x, y) {
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        };
    }
"""

replacements = {
    " ": "_",      # Replace spaces with underscores
    "@": "at",     # Replace "@" with "at"
    ",": "",       # Remove commas
    ":": "-",      # Replace colons with dashes
    "✔": "",       # Remove special characters
}

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
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Disable browser notifications
    chrome_options.add_argument("--disable-popup-blocking")  # Block pop-ups
    chrome_options.add_argument("--disable-gpu")  # Optional for headless

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
                    close_element = driver.find_element(By.CSS_SELECTOR, "svg.bx-close-xsvg")
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

def plays_to_df(shots, video_file):
    df = pd.DataFrame(shots)
    df['VIDEO_FILE'] = video_file
    # df.to_csv('plays.csv')
    return df

def get_video(index, plays, play_container, page, videos):
    video_filename = ''
    # get_page()
    # with open('page.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    # page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    video_tag = soup.find('video')
    video_url = video_tag.get('src')
    videos.append(videos)
    # if video_url in videos:
    #     time.sleep(3)
    print("video_url", video_url)
    # Download the video using requests
    if video_url:
        # for play in plays:
        # print("Video URL:", video_url)
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            # Save the video to a file
            # print('index: ', plays[index])
            directory = plays[index]["PLAYER"]
            if not os.path.exists(directory):
                os.makedirs(directory)
            video_filename = "".join(str(value).strip() for value in plays[index].values()) + ".mp4"
            cleaned_filename = multiple_replace(video_filename, replacements)
            file_path = os.path.join(directory, cleaned_filename)
            with open(file_path, "wb") as video_file:
                for chunk in tqdm(response.iter_content(chunk_size=1024)):
                    video_file.write(chunk)
            print('video path: ', file_path)
        except Exception as e:
            print(f"Failed to download the video: {e}")
    else:
        print("No source URL found for the video element.")
        video_filename = "default_video.mp4"
    return cleaned_filename

def hide_banners(driver):
    scripts = ["""
    var elements = document.querySelectorAll('.bx-align');
    elements.forEach(function(element) {
        element.remove();  // Removes all elements with class 'bx-creative'
        });
    ""","""
    var elements = document.querySelectorAll('.bx-creative');
    elements.forEach(function(element) {
        element.remove();  // Removes all elements with class 'bx-creative'
        });
    ""","""
    document.querySelector('div[role=\"alertdialog\"]').style.display = 'none';
    """]

    for script in scripts:
        if driver.find_elements(By.CLASS_NAME, "bx-slab"):
            driver.execute_script("""
            document.querySelector(".bx-slab").remove();
            """)
            print(".bx-slab element is present on the page.")
        driver.execute_script(script)

def click_element(driver):
    try:
        # Find the element (tr) using XPath
        tr_element = driver.find_element(By.XPATH, '//tr[@class="EventsTable_row__Gs8B9" and @data-is-playing="true"]')

        # Use JavaScript to click the element directly
        driver.execute_script("arguments[0].click();", tr_element)
        print("Element clicked successfully without scrolling!")
        
    except Exception as e:
        print(f"Error clicking the element: {e}")
        with open("errorlog.txt", 'a') as f:
            f.write(f'Error clicking the element: {e}\n')


if __name__ == "__main__":
    get_page()
    # get_plays()
    # get_page()
    # get_video()
    # plays_to_df()






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

# def get_data():
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

# def get_page():
#     # chrome_options.add_argument("--headless")  # Run in headless mode
#     # chrome_options.add_argument("--disable-gpu")  # Disable GPU (optional for headless)
#     driver = webdriver.Chrome(options=chrome_options)
#     # Navigate to Google's homepage
#     driver.get(url)
#     driver.execute_script(cursor_script)
#     # time.sleep(5)
#     wait = WebDriverWait(driver, 10)
#     time.sleep(2)
#     video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
#     # video_element = driver.find_element(By.TAG_NAME, "video")
    
#     # Inject JavaScript to pause the video
#     driver.execute_script("arguments[0].pause();", video_element)
#     print("Video paused successfully!")
#     print("Page is loaded, and the <video> element is available.")
#   # Wait for the results to load and display the title
#     # driver.implicitly_wait(20)  # Wait up to 5 seconds for elements to appear
#   # print(driver.title)
#     render = driver.page_source
#     # soup = BeautifulSoup(render, 'html_parser')
#     shots, play_container = get_plays(render)
#     for index,play in enumerate(play_container):
#         try:
#             # Find the <tr> element using its class and attribute
#             # tr_element = driver.find_element(By.XPATH, '//tr[@class="EventsTable_row__Gs8B9"]')
#             target_element = driver.find_element(By.XPATH, '//td[@class="Crom_stickyRank__aN66p"]')

#             # class="Crom_stickyRank__aN66p"
#             # Change the 'data-is-playing' attribute to 'false' using JavaScript
#             # driver.execute_script('arguments[0].setAttribute("data-is-playing", "true");', tr_element)

#             # Verify the change
#             # updated_value = tr_element.get_attribute("data-is-playing")
#             # print("Updated data-is-playing value:", updated_value)
#             # Scroll to the element if it's not visible
#             driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
#             # Wait until the element is clickable
#             # tr_element = WebDriverWait(driver, 10).until(
#             #     EC.element_to_be_clickable((By.XPATH, '//tr[@class="EventsTable_row__Gs8B9" and @data-is-playing="true"]'))
#             # )
#             move_cursor_to_element(driver, target_element)
#             # Use JavaScript to simulate the click
#             driver.execute_script("arguments[0].click();", target_element)
#             print("Element clicked via JavaScript!")
#             # Click the element
#             # tr_element.click()
#             # click_element(tr_element)
#             time.sleep(1)
#             video_file = get_video(index, play, play_container, render)
#             # for shot in shots:
#             #     shot['video_file'] = video_file