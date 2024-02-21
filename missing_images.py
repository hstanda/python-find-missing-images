import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

def get_all_links(url):
    # Make a GET request to the URL
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anchor tags in the HTML
        anchor_tags = soup.find_all('a')
        
        # Extract the href attribute from each anchor tag
        links = [a.get('href') for a in anchor_tags if a.get('href')]
        
        return links
    
    else:
        print(f"Error: Unable to fetch the URL. Status code: {response.status_code}")
        return None

def find_missing_images(url, save_path='./images', visited_images_set=None, missing_images_set=None):
    # Make a GET request to the website
    response = requests.get(url)
    print(url)
    time.sleep(5)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image tags in the HTML
        img_tags = soup.find_all('img')
        
        # Create the directory to save images if it doesn't exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        missing_images = []
        
        # Iterate through each image tag
        for img_tag in img_tags:
            # Get the source (src) attribute of the image
            img_src = img_tag.get('src')
            
            # Check if the image file exists locally
            img_path = os.path.join(save_path, os.path.basename(img_src))
            
            if not os.path.exists(img_path) and img_src not in visited_images_set:
                missing_images.append(img_src)
                visited_images_set.add(img_src)
                
                # Append the missing image path to a text file
                with open('missing_images.txt', 'a') as file:
                    file.write(img_src + '\n')
                
        return missing_images
    
    else:
        print(f"Error: Unable to fetch the website. Status code: {response.status_code}")
        return None

def find_missing_images_on_website(base_url, save_path='./images'):
    # Create the directory to save images if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # List to store all URLs to visit
    urls_to_visit = [base_url]
    visited_urls = set()
    visited_images_set = set()
    
    missing_images_set = set()

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        visited_urls.add(current_url)

        # Get all links on the current page
        links = get_all_links(current_url)

        if links:
            for link in links:
                # Join the base URL with the relative link
                absolute_link = urljoin(current_url, link)

                # Check if the link is from the same domain and hasn't been visited yet
                if urlparse(absolute_link).netloc == urlparse(base_url).netloc and absolute_link not in visited_urls:
                    urls_to_visit.append(absolute_link)

            # Find missing images on the current page
            find_missing_images(current_url, save_path, visited_images_set, missing_images_set)

    return list(missing_images_set)

# Example usage:
website_url = 'https://harjeevansingh.com/'
missing_images = find_missing_images_on_website(website_url)

if missing_images:
    print("Missing Images added to file")
else:
    print("No missing images found.")
