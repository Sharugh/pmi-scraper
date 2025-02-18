import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape report dates
def scrape_pmi_report_dates():
    base_url = "https://www.cbsl.gov.lk/en/search/node/SL%20Purchasing%20Managers%E2%80%99%20Index%20%28PMI%29?page="
    report_dates = []

    # Iterate through multiple pages to get all dates
    for page in range(0, 10):  # Adjust the range if more pages exist
        url = base_url + str(page)
        response = requests.get(url)
        if response.status_code != 200:
            break  # Stop if the page does not load properly

        soup = BeautifulSoup(response.text, "html.parser")
        # Find all links that contain PMI reports
        for link in soup.find_all("a", href=True):
            if "Purchasing Managers' Index" in link.text:
                report_dates.append(link.text.strip())

    return report_dates

# Streamlit UI
st.title("SL Purchasing Managers’ Index (PMI) Report Dates")
st.write("Scraping available report dates from CBSL website...")

# Scrape report dates
report_dates = scrape_pmi_report_dates()

# Display results
if report_dates:
    df = pd.DataFrame({"Report Dates": report_dates})
    st.dataframe(df)
else:
    st.write("No PMI reports found.")

st.write("Data sourced from the Central Bank of Sri Lanka (CBSL).")

