import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from requests_html import HTMLSession

# Function to fetch search results
def fetch_search_results(base_url, search_url, keyword):
    session = HTMLSession()
    pdf_links = []

    for page in range(1, 7):  # Looping through 6 pages
        url = f"{search_url}?page={page}"
        response = session.get(url)
        response.html.render(timeout=30)  # Render JavaScript
        soup = BeautifulSoup(response.html.html, "html.parser")

        # Find all links in search results
        for link in soup.find_all("a", href=True):
            if keyword.lower() in link.text.lower():
                full_url = base_url + link["href"] if not link["href"].startswith("http") else link["href"]
                pdf_links.append(full_url)

    return pdf_links

# Function to find "FULL TEXT" PDF links inside each search result
def find_pdf_links(url):
    session = HTMLSession()
    response = session.get(url)
    response.html.render(timeout=30)
    soup = BeautifulSoup(response.html.html, "html.parser")

    pdf_url = None
    for link in soup.find_all("a", href=True):
        if "FULL TEXT" in link.text.upper():  # Clicking on "FULL TEXT"
            pdf_url = link["href"]
            if not pdf_url.startswith("http"):
                pdf_url = url.rsplit("/", 1)[0] + "/" + pdf_url
            break

    return pdf_url

# Function to download PDFs
def download_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            filename = pdf_url.split("/")[-1]
            with open(filename, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    pdf_file.write(chunk)
            return filename
        return None
    except:
        return None

# Streamlit UI
st.title("📄 CBSL PMI PDF Scraper & Downloader")
st.write("This tool extracts and downloads PDFs from CBSL search results.")

# User inputs
base_url = "https://www.cbsl.gov.lk"
search_url = "https://www.cbsl.gov.lk/en/search/node/SL%20Purchasing%20Managers%E2%80%99%20Index%20%28PMI%29"
keyword = "SL Purchasing Managers’ Index (PMI)"

if st.button("🔍 Search for PDFs"):
    st.write("🔎 Searching for PMI reports... Please wait.")
    
    # Scrape search results
    result_links = fetch_search_results(base_url, search_url, keyword)

    if result_links:
        st.success(f"✅ Found {len(result_links)} reports! Extracting PDFs...")

        pdf_data = []
        for result in result_links:
            pdf_link = find_pdf_links(result)
            if pdf_link:
                pdf_data.append({"Report Link": result, "PDF Link": pdf_link})

        # Convert to DataFrame and display
        df = pd.DataFrame(pdf_data)
        st.dataframe(df)

        # Allow user to select and download PDFs
        if not df.empty:
            selected_pdf = st.selectbox("📂 Select a PDF to download:", df["PDF Link"].tolist())
            if st.button("⬇️ Download PDF"):
                filename = download_pdf(selected_pdf)
                if filename:
                    with open(filename, "rb") as file:
                        st.download_button(label="📥 Click to Download", data=file, file_name=filename, mime="application/pdf")
                else:
                    st.error("⚠️ Failed to download the PDF. Try another one.")
    else:
        st.error("❌ No reports found.")

st.write("📌 Works on CBSL search results for PMI reports.")
