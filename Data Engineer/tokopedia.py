import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os


#Setup for running Chrome Driver

titles = []
prices = []
sellers = []
locations = []
sold_infos = []
ratings = []
links = []

def webscrap_tokopedia():
    driver = webdriver.Chrome()
    driver.maximize_window()
    for i in range(1,11):
        # Masuk ke Link dengan selenium (Extract URL)
        url = "https://www.tokopedia.com/search?navsource=home&page={}&q=perak%201oz&&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=product".format(i)
        driver.get(url)


        # Membuat fungsi scroll down agar bisa scroll page kebawah 
        def scroll_down():
            # Scroll down dengan fungsi yang sama dengan tombol keyboard PAGE DOWN
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)  # Menambah Delay 1s agar halaman bisa ke load

        # Jumlah berapa kali fungsi scroll dilakukan
        scrolls = 8  # angka untuk menentukan jumlah fungsi scroll
        for _ in range(scrolls):
            scroll_down()

        # Mengambil konten dari HTML dengan driver
        html_content = driver.page_source

        # Menggunakan parsing HTML dengan beautifulsoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Mencari element tag dan class yang relevan untuk di extract
        product_containers = soup.find_all('div', class_='css-llwpbs')


        for product in product_containers:
            title = product.find('div', class_='prd_link-product-name') #Mencari product pada tag div dan class prd_link-product-name dan menyimpan pada variable title
            price = product.find('div', class_='prd_link-product-price') #Mencari price pada tag div dan class prd_link-product-price dan menyimpan pada variable price
            seller_info = product.find('div', class_='css-1rn0irl') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info
            sold_info = product.find('span', class_='prd_label-integrity') #Mencari jumlah produk terjual pada tag span dan class prd_label-integrity dan menyimpan pada variable sold_info
            rating = product.find('span', class_='prd_rating-average-text') #Mencari product pada tag span dan class prd_rating-average-text dan menyimpan pada variable rating
            link =  product.find('div', class_='css-1f2quy8').find('a') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info

            #Memanggil fungsi mengambil Text (get_text()) dan menambahkan serta menyimpan pada variable list
            if title and price and seller_info:
                titles.append(title.get_text())
                prices.append(price.get_text())
                links.append(link.get('href'))
                sellers.append(seller_info.find('span', class_='prd_link-shop-name').get_text())
                locations.append(seller_info.find('span', class_='prd_link-shop-loc').get_text())
            else:
                continue

            if sold_info:
                sold_infos.append(sold_info.get_text())
            else:
                sold_infos.append(None)

            if rating:
                ratings.append(rating.get_text())
            else:
                ratings.append(None)


    # Menutup browser setelah web scraping
    driver.quit()

    # Membuat dataframe dari data yang sudah dikumpulkan
    data = pd.DataFrame({
        'product_name': titles,
        'price': prices,
        'seller': sellers,
        'location': locations,
        'number_sold': sold_infos,
        'rating': ratings,
        'link': links,
    })
    #Menyimpan data raw
    data.to_csv('Tokped_raw.csv',index=False)

def clean_tokopedia():
    # Load the raw data
    data = pd.read_csv('Tokped_raw.csv')


    data = data.dropna()
    # Clean and extract the numeric part of the price
    data['price'] = data['price'].str.replace('Rp', '').str.replace('.', '').str.replace('rb', '000')
    data['price'] = data['price'].str.extract(r'(\d+)').astype(int)

    # Clean and extract the numeric part of the "Number Sold"
    data['number_sold'] = data['number_sold'].str.replace('terjual', '').str.replace('+', '')
    data['number_sold'] = data['number_sold'].str.replace('rb', '000').str.extract(r'(\d+)').astype(int)

    # Fill missing values in the "Rating" column with 0
    data['rating'].fillna(0, inplace=True)

    # Convert the "Rating" column to float
    data['rating'] = data['rating'].astype(float)

    data.to_csv('Tokopedia_clean.csv')


    

if __name__ == '__main__':
    webscrap_tokopedia()
    clean_tokopedia()