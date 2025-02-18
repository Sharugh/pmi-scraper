import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Function to scrape PDF links
def scrape_pdfs(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".pdf"):
                pdf_links.append(href if href.startswith("http") else url + href)

        return pdf_links
    except Exception as e:
        return str(e)

# Function to download PDFs
def download_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            filename = pdf_url.split("/")[-1]
            with open(filename, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        pdf_file.write(chunk)
            return filename
        else:
            return None
    except Exception as e:
        return None

# Streamlit UI
st.title("PDF Scraper & Downloader")
st.write("Enter a website URL to extract and download PDFs.")

# User input for the website URL
url = st.text_input("Enter the website URL (including https://):")

if url:
    st.write("Searching for PDFs... Please wait.")
    pdf_links = scrape_pdfs(url)

    if pdf_links:
        st.success(f"Found {len(pdf_links)} PDFs!")
        
        # Search bar for filtering PDFs
        search_query = st.text_input("Search for a PDF (optional):")
        if search_query:
            pdf_links = [link for link in pdf_links if search_query.lower() in link.lower()]

        # Display the PDFs
        df = pd.DataFrame({"PDF Links": pdf_links})
        st.dataframe(df)

        # Download option
        selected_pdf = st.selectbox("Select a PDF to download:", pdf_links)
        if st.button("Download PDF"):
            filename = download_pdf(selected_pdf)
            if filename:
                with open(filename, "rb") as file:
                    st.download_button(label="Click to Download", data=file, file_name=filename, mime="application/pdf")
            else:
                st.error("Failed to download the PDF. Try another one.")

    else:
        st.error("No PDFs found on this website.")

st.write("📌 This tool works on any website that hosts PDFs.")
