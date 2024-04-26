#pip install beautifulsoup4
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

def scrape_crossRef(keywords):
    results = []
    seen = set()  # Set to keep track of unique (title, author) tuples

    for keyword in keywords:
        page = 1  # Start from the first page
        #If you want every page that is displayed, you can change to "while TRUE" instead of page < n
        while page < 3:
            # Construct the URL for each keyword and page
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://search.crossref.org/search/works?q={encoded_keyword}&from_ui=yes&page={page}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Failed to fetch page for keyword '{keyword}' at page {page}. Status code: {response.status_code}")
                break  # Stop if the page request fails

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('tr', class_='full-docsum')
            if not articles:
                break  # Stop if no articles found on the page

            for article in articles:
                title_elem = article.find('a', class_='docsum-title')
                author_elem = article.find('span', class_='docsum-authors full-authors')
                if title_elem and author_elem:
                    title = title_elem.text.strip()
                    author = author_elem.text.strip()
                    unique_identifier = (title)  # Tuple of title and author

                    if unique_identifier not in seen:
                        seen.add(unique_identifier)  # Mark this identifier as seen
                        result = {
                                "title": title,
                                "author": author
                            }
                        results.append(result)
            page += 1  # Move to the next page

    return results

# Keywords to search for
#Single cell taken out (3000+ results )
#Multiplexed imaging, CODEX, Phenocycler, MIBI, CycIF, spatial proteomics, spatial transcriptomics, single-cell, spatial data, immune cells, T cells, tissue atlas, spatial mapping.
#Can change keywords whenever
keywords = ["Spatial+omics", "CODEX", "Multiplexed Imaging", "MIBI", "CycIF", "IBEX", "Phenocycler", "MIBI", "spatial+proteomics", "spatial+data", "immune+cells", "spatial+mapping", "tissue+atlas"]

# Run the scraper and get results
search_results = scrape_crossRef(keywords)

if search_results:
    # Specify the filename
    filename = "/Users/charliekonen/Desktop/scraper/scraped_articles_crossRef.csv"

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