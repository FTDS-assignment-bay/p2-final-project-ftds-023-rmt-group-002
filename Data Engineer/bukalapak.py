import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os

#Setup untuk menjalankan Chrome Driver

titles = []
prices = []
sellers = []
locations = []
sold_infos = []
ratings = []
links = []

def webscrap_bukalapak():
    driver = webdriver.Chrome()
    driver.maximize_window()
    for i in range(1,4):
        # Masuk ke Link dengan selenium (Extract URL)
        url = "https://www.bukalapak.com/products?page={}&search%5Bkeywords%5D=perak%201%20oz".format(i)
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
        product_containers = soup.find_all('div', class_='bl-flex-item mb-8')


        for product in product_containers:
            title = product.find('p', class_='bl-text bl-text--body-14 bl-text--secondary bl-text--ellipsis__2') #Mencari product pada tag div dan class prd_link-product-name dan menyimpan pada variable title
            price = product.find('p', class_='bl-text bl-text--semi-bold bl-text--ellipsis__1 bl-product-card-new__price') #Mencari price pada tag div dan class prd_link-product-price dan menyimpan pada variable price
            seller = product.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-text--ellipsis__1 bl-product-card-new__store-name') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info
            location = product.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-text--ellipsis__1 bl-product-card-new__store-location')
            sold_info = product.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-product-card-new__sold-count') #Mencari jumlah produk terjual pada tag span dan class prd_label-integrity dan menyimpan pada variable sold_info
            rating = product.find('p', class_='bl-text bl-text--caption-12 bl-text--bold') #Mencari product pada tag span dan class prd_rating-average-text dan menyimpan pada variable rating
            link =  product.find('p', class_='bl-text bl-text--body-14 bl-text--secondary bl-text--ellipsis__2').find('a') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info

            #Memanggil fungsi mengambil Text (get_text()) dan menambahkan serta menyimpan pada variable list
            if title and price and 'seller_info':
                titles.append(title.get_text().strip('\n'))
                prices.append(price.get_text().strip('\n'))
                links.append(link.get('href'))
                sellers.append(seller.get_text().strip('\n'))
                locations.append(location.get_text().strip('\n'))
            else:
                continue

            if sold_info:
                sold_infos.append(sold_info.get_text().strip('\n'))
            else:
                sold_infos.append(None)

            if rating:
                ratings.append(rating.find('a', class_='bl-link').get_text().strip('\n'))
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
    #Save raw data
    data = data.apply(lambda x: x.str.replace('\n', ''))
    data = data.apply(lambda x: x.str.strip())
    data.to_csv('BulakMas_raw.csv',index=False)

def clean_bukalapak():
    data = pd.read_csv('BulakMas_raw.csv')
    #Clean \n in every columns
    data['product_name'] = data['product_name'].str.strip()
    #Mengubah Kolom "Price" menjadi tipe integer
    data['price'] = data['price'].str.replace(".","").astype(int)
    #Mengubah Kolom "Number Sold" menjadi tipe numerik dan extract value
    data['number_sold'] = data['number_sold'].str.replace("Terjual","").str.replace("+","").str.replace("rb","000")
    data['number_sold'].fillna('0', inplace=True)
    data['number_sold'] = data['number_sold'].astype(int)


    #Mengisi missing value pada Rating dengan rata rata seluruh rating
    data['rating'].fillna('0', inplace=True)
    #Mengubah Kolom "Rating" menjadi tipe data float
    data['rating']= data['rating'].astype(float)

    data.to_csv('Bukalapak_clean.csv')
    

if __name__ == '__main__':
    webscrap_bukalapak()
    clean_bukalapak()