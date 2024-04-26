#pip install beautifulsoup4
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import time  # Import the time module


#currently blocked. Add delay or something to slow things down. Check back later
def scrape_googscholar(keywords):
    results = []
    seen = set()  # Set to keep track of unique (title, author) tuples

    for keyword in keywords:
        page = 0  # Start from the first page
        #If you want every page that is displayed, you can change to "while TRUE" instead of page < n
        #For google scholar, we can't control page size (only 10 per page)
        #200 here is adjustable and represents how many studies will be looked at 
        while page < 100:
            # Construct the URL for each keyword and page
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://scholar.google.com/scholar?start={page}&q={encoded_keyword}&hl=en&as_sdt=0,34&as_ylo=2019&as_yhi=2024"

            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to fetch page for keyword '{keyword}' at page {page}. Status code: {response.status_code}")
                break  # Stop if the page request fails

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('div', class_='gs_ri')
            if not articles:
                break  # Stop if no articles found on the page

            for article in articles:
                title_elem = article.find('h3', class_='gs_rt')
                author_elem = article.find('div', class_='gs_a')
                if title_elem and author_elem:
                    title = title_elem.text.strip()
                    # Clean title for potential 'Cite' prefix or '[PDF]' annotations
                    title = title.replace('[PDF]', '').replace('[HTML]', '').strip()
                    author = author_elem.text.split('-')[0].strip()  # Author info before the dash
                    unique_identifier = title

                    if unique_identifier not in seen:
                        seen.add(unique_identifier)  # Mark this identifier as seen
                        result = {
                                "title": title,
                                "author": author
                            }
                        results.append(result)
            page += 10  # Move to the next page
            #added to prevent 429 error
            time.sleep(5)  # Delay of 5 seconds before the next request

    return results

#The format I used was mainly like Assay + field name + single-cell + specific aims. Like {Multiplexed imaging, CODEX, Phenocycler, MIBI, CycIF}
#  + {spatial proteomics, spatial transcriptomics} + single-cell + 
# {immune cells, T cells, tissue atlas, spatial mapping} choose one from the brackets for different combinations.

Assay = ["Multiplexed+imaging", "CODEX", "Phenocycler", "MIBI", "CycIF"]
field_name = ["spatial+proteomics", "spatial+transcriptomics"]
single_cell = ["single+cell"]
spec_aim = ["immune+cells", "T+cells", "tissue+atlas", "spatial+mapping"]

keywords = []  # Initialize an empty list to store the combinations

for assay in Assay:
    for field in field_name:
        for cell in single_cell:
            for aim in spec_aim:
                combo = assay + "+" + field + "+" + cell + "+" + aim
                keywords.append(combo)  # Add the combo to the keywords list

search_results = scrape_googscholar(keywords)

if search_results:
    # Specify the filename
    filename = "/Users/charliekonen/Desktop/scraper/scraped_articles_google_scholar.csv"

    # Writing to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Writing the header
        writer.writerow(["Title", "Author"])
        
        # Writing article data
        for article in search_results:
            writer.writerow([article["title"], article["author"]])
            
    print(f"Results successfully saved to {filename}")
else:
    print("No results found.")