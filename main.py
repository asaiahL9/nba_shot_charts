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
from lxml import etree
import lxml
import functools                                        # used to create a print function that flushes the buffer
flushprint = functools.partial(print, flush=True)       # create a print function that flushes the buffer immediately



player_id = '203999'
team_id = '1610612743'
game_id = '0022400350'
url = f'https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID={game_id}&PlayerID={player_id}&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID={team_id}&flag=3&sct=plot&section=game'
irl = f'0https://www.nba.com/stats/events?CFID=&CFPARAMS=&ContextMeasure=FGA&EndPeriod=0&EndRange=31800&GameID=0022400350&PlayerID=203999&RangeType=0&Season=2024-25&SeasonType=Regular%20Season&StartPeriod=0&StartRange=0&TeamID=1610612743&flag=3&sct=plot&section=game'
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')
# with open('shot_chart.html', 'w') as f:
#   f.write(soup.prettify())
# container = soup.find('div', class_="x1cy8zhl x9f619 x78zum5 xl56j7k x2lwn1j xeuugli x47corl")
# list = soup.find_all('div', class_='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1')
# followers = soup.find_all('div', class_ = "xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6")
# print(container)
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

def find_chart():
    with open('shot_chart.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    soup.find()
    chart = soup.find("g", class_ = "court")
    return chart
#    <rect fill="#f3f7fd" x="-20" y="-20" width="540" height="510"></rect>

def get_shots():
    with open('shot_chart.svg', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(page, 'lxml') # #parsing svg content
    shots = soup.find_all("g", class_ = "shot")
    with open('shots.svg', 'w', encoding='utf-8') as f:
        for shot in shots:
            f.write(str(shot) +'\n')
            # print(shot)
    print(len(shots))
    return shots

def get_shot_chart():
    with open('shot_chart.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(page, 'html.parser') # #parsing html content
    svgs = soup.find_all("svg")
    # svg_element = soup.find("svg", viewBox="0,0,540,570")
    with open('shot_chart.svg', 'w', encoding='utf-8') as f:
        f.write(str(svgs[8]))
        # for svg in svgs:
        #     f.write(str(svg) + '\n')
    

def get_coords():
    # Parse the HTML with BeautifulSoup
    with open('shot_chart.svg', 'r', encoding='utf-8') as f:
        html_content = f.read()
    page = html_content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all elements with the 'transform' attribute
    transform_elements = soup.find_all(attrs={"transform": True})

    # Extract the transform attribute values
    transform_values = [element["transform"] for element in transform_elements]
    with open("coords.txt", 'w') as f:
        for value in transform_values:
            f.write(value + '\n')
        # f.write(str(transform_values))
    # Print all transform values
    print(transform_values)

def add_buttons():
    # Parse the HTML with BeautifulSoup
    with open('shot_chart.svg', 'r', encoding='utf-8') as f:
        svg_content = f.read()
    page = svg_content
    soup = BeautifulSoup(svg_content, 'html.parser')
    root = etree.fromstring(svg_content)

    # Find all shot <g> elements
    shots = root.xpath('//svg:g[@class="shot"]', namespaces={'svg': 'http://www.w3.org/2000/svg'})

    # Loop through each shot and add a button (this will just create a simple clickable rectangle for demonstration)
    for shot in shots:
        # Extract the position from the transform attribute of the <path> tag
        transform = shot.xpath('.//svg:path/@transform', namespaces={'svg': 'http://www.w3.org/2000/svg'})[0]
        # Example of extracting translate(x, y) from transform (for this example assume only translation is used)
        translate_values = transform.split('(')[1].split(')')[0].split(',')
        x = float(translate_values[0].strip())
        y = float(translate_values[1].strip())
        
        # Create a button element at the same position
        button = etree.Element('rect', {
            'x': str(x - 10),  # Adjust x and y for button size
            'y': str(y - 10),
            'width': '100',
            'height': '100',
            'fill': 'rgba(0, 0, 0, 10)',
            'stroke': 'rgba(0, 0, 0, 0.8)',
            'stroke-width': '2',
            'onclick': f"alert('Shot at {x},{y}')"
        })
        
        # Append the button to the shot group (you can also use <button> or other elements)
        shot.append(button)

    # Convert back to a string and print the modified SVG content
    modified_svg_content = etree.tostring(root, pretty_print=True).decode()
    with open("shotbuttons.svg","w") as f:
        f.write(modified_svg_content)
    print(modified_svg_content)

if __name__ == "__main__":
#   get_data()
#   chart = find_chart()
#   print(chart)
    # get_shots()
#   print(shots)
    # get_shot_chart()
    # get_coords()
    add_buttons()