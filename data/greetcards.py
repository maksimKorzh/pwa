####################################
#
#    Script to scrape greetcards
#    from  https://otkrytki.top/
#
####################################

# Packages
import requests
from bs4 import BeautifulSoup
import time
import json
import csv
import os

# Debug mode:
DEBUG = False

# Web browser name
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"

# Fetch data from target URL
def fetch(url, filename):
    # Try extract data
    try:
        # Response holder
        response = None

        # Load HTML from file
        if DEBUG:
            # Parse HTML if exists
            if os.path.isfile(filename):
                with open(filename, encoding="utf-8") as f: response = f.read()
                print(f"Data loaded from {filename}")
            
            # Fetch HTML otherwise
            else:
                response = requests.get(url, headers={"user-agent": USER_AGENT}).text
                with open(filename, "w", encoding="utf-8") as f: f.write(response)
                print(f"Fetched data from {url}")

        # Load HTML from target URL
        else:
            response = requests.get(url, headers={"user-agent": USER_AGENT}).text
            print(f"Fetched data from {url}")
        
        # Parse HTML
        return BeautifulSoup(response, "lxml")
    
    # Print error on failure
    except Exception as e: print(repr(e));

# Build greetcards database
def fetch_greetcards():
    # Print debug mode
    print(f"Debug mode is {"on" if DEBUG else "off"}")

    # Get category URLs
    data = fetch("https://otkrytki.top/", "categories.html")
    categories = data.find("ul", {"id": "primary-menu"}).find_all("li")
    category_urls = [i.find("a")["href"] for i in categories if "https" in i.find("a")["href"]]

    # Loop over category URLs
    for category in category_urls:
        # Get pagination data
        data = fetch(category, "pagination.html")

        # Get number of total pages
        try: total_pages = max([int(i.text) for i in data.find_all("a", {"class": "page-numbers"}) if i.text])
        except: total_pages = 1
        
        # Print total pages
        print(f"Total pages: {total_pages}")
        
        # Loop over page URLs
        for page in range(1, total_pages+1):
            # Delay between requests
            time.sleep(1)
            
            # Build page URL
            page_url = category + "page/" + str(page)
            
            # Get page data
            data = fetch(page_url, str(page) + ".html")

            # Get greetcards
            greetcards = data.find_all("img", {"class": "attachment-post-thumbnail size-post-thumbnail wp-post-image"})
            
            # Loop over greetcards
            for card in greetcards:
                # Attempt extracting greetcard data
                try:
                    # Extract features
                    features = {
                        "title": card["title"],
                        "url": card["src"]
                    }
                    
                    # Store greetcard to CSV
                    with open("greetcards.csv", "a", newline="", encoding="utf-8") as f:
                        csv_writer = csv.DictWriter(f, fieldnames=features.keys())
                        csv_writer.writerow(features)

                # Fallback on error
                except Exception as e: print(repr(e));

# Run script
fetch_greetcards()