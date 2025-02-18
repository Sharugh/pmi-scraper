import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Function to set up Selenium WebDriver
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to scrape PDFs with Selenium (for dynamic pages)
def scrape_pdfs_selenium(url, keyword):
    driver = get_driver()
    driver.get(url)
    time.sleep(3)  # Allow page to load

    # Click "See more" or similar buttons if present
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'See more')]")
        for button in buttons:
            button.click()
            time.sleep(2)  # Wait for new content to load
    except:
        pass

    # Extract PDF links
    soup = BeautifulSoup(driver.page_source, "html.parser")
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower() and keyword.lower() in link.text.lower():
            pdf_links.append(href if href.startswith("http") else url + href)

    driver.quit()
    return pdf_links

# Function to scrape PDFs using BeautifulSoup (for static pages)
def scrape_pdfs_bs(url, keyword):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
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
                    if chunk:
                        pdf_file.write(chunk)
            return filename
        else:
            return None
    except Exception as e:
        return None

# Streamlit UI
st.title("📄 Advanced PDF Scraper & Downloader")
st.write("Enter a website URL and keyword to search and download PDFs.")

# User inputs
url = st.text_input("🔗 Enter the website URL (including https://):")
keyword = st.text_input("🔍 Enter the keyword present in the website:")

if url and keyword:
    st.write("🔎 Searching for PDFs... Please wait.")
    
    # Try both scraping methods
    pdf_links = scrape_pdfs_selenium(url, keyword) + scrape_pdfs_bs(url, keyword)

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

st.write("📌 Works on both static and dynamic websites.")
