import requests
from bs4 import BeautifulSoup
import re

url = "https://www.marseille.fr/logement-urbanisme/am%C3%A9lioration-de-lhabitat/arretes-de-peril" 
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

def clean_text(text):
    text = re.sub(r'\u200B', '', text) # Remove zero-width space characters (Unicode \u200B)
    text = text.strip()  # Remove leading and trailing whitespace
    return text

# Extract the quarters and streets names
quarters = soup.find_all('dt')
for quarter in quarters:
    all_streets_quarter = quarter.find_next_sibling('dd')
    streets = all_streets_quarter.find_all('p')
    print('\n', quarter.get_text())
    for street in streets:
        street_name = street.get_text().strip()
        if street_name and not street_name.startswith('-'):
            print(clean_text(street_name))

