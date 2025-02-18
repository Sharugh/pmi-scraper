import os
os.system("pip install lxml[html_clean] lxml_html_clean --quiet")
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from requests_html import HTMLSession  # Works on Streamlit Cloud

# Function to scrape PDFs (handles JavaScript rendering)
def scrape_pdfs(url, keyword):
    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render(timeout=30)  # Render JavaScript
        soup = BeautifulSoup(response.html.html, "html.parser")

        pdf_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if ".pdf" in href.lower() and keyword.lower() in link.text.lower():
                pdf_links.append(href if href.startswith("http") else url + href)

        return pdf_links
    except Exception as e:
        return []

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
st.title("📄 PDF Scraper & Downloader (Streamlit Cloud Compatible)")
st.write("Enter a website URL and keyword to search and download PDFs.")

# User inputs
url = st.text_input("🔗 Enter the website URL (including https://):")
keyword = st.text_input("🔍 Enter the keyword present in the website:")

if url and keyword:
    st.write("🔎 Searching for PDFs... Please wait.")
    
    # Scrape PDFs
    pdf_links = scrape_pdfs(url, keyword)

    if pdf_links:
        st.success(f"✅ Found {len(pdf_links)} PDFs related to '{keyword}'!")

        # Display PDFs in a dataframe
        df = pd.DataFrame({"PDF Links": pdf_links})
        st.dataframe(df)

        # Select and download PDFs
        selected_pdf = st.selectbox("📂 Select a PDF to download:", pdf_links)
        if st.button("⬇️ Download PDF"):
            filename = download_pdf(selected_pdf)
            if filename:
                with open(filename, "rb") as file:
                    st.download_button(label="📥 Click to Download", data=file, file_name=filename, mime="application/pdf")
            else:
                st.error("⚠️ Failed to download the PDF. Try another one.")
    else:
        st.error("❌ No PDFs found with the given keyword.")

st.write("📌 Works on both static and JavaScript-rendered websites.")
