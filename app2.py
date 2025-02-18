import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to scrape the website and extract dates
def scrape_pmi_dates(base_url, search_query):
    dates = []
    for page in range(5):  # Assuming there are 5 pages
        url = f"{base_url}/en/search/node/{search_query}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result items
        results = soup.find_all('div', class_='search-result')
        
        for result in results:
            title = result.find('h3').text
            link = result.find('a')['href']
            full_link = urljoin(base_url, link)
            
            # Extract date from the title or link (assuming date is in the title)
            date = title.split()[-1]  # Adjust this based on the actual format
            dates.append((date, full_link))
    
    return dates

# Streamlit app
def main():
    st.title("SL Purchasing Managers’ Index (PMI) Reports")
    
    base_url = "https://www.cbsl.gov.lk"
    search_query = "SL Purchasing Managers’ Index (PMI)"
    
    st.write(f"Scraping {base_url} for PMI reports...")
    
    dates = scrape_pmi_dates(base_url, search_query)
    
    if dates:
        st.write("### Available Reports:")
        for date, link in dates:
            st.write(f"- **Date:** {date} - [Download PDF]({link})")
    else:
        st.write("No reports found.")

if __name__ == "__main__":
    main()