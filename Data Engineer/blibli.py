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


def webscrap_blibli():
    driver = webdriver.Chrome()
    while True:
        try:
            driver = webdriver.Chrome()
            driver.maximize_window()
            for i in range(1,2):
                # Masuk ke Link dengan selenium (Extract URL)
                url = "https://www.blibli.com/cari/perak%201%20oz?category=LO-1000074&category=GO-1000145&category=LO-1000056&sort=0&page={}&start=0".format(i)
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
                product_containers = soup.find_all('div', class_='product__card product__card__five')


                for product in product_containers:
                    title = product.find('div', class_='blu-product__name') #Mencari product pada tag div dan class prd_link-product-name dan menyimpan pada variable title
                    price = product.find('div', class_='blu-product__price-after') #Mencari price pada tag div dan class prd_link-product-price dan menyimpan pada variable price
                    seller_info = product.find('div', class_='blu-product__location-text blu-product__location--interaction') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info
                    sold_info = product.find('div', class_='blu-product__sold') #Mencari jumlah produk terjual pada tag span dan class prd_label-integrity dan menyimpan pada variable sold_info
                    rating = product.find('div', class_='blu-product__rating') #Mencari product pada tag span dan class prd_rating-average-text dan menyimpan pada variable rating
                    # link =  product.find('div', class_='css-1f2quy8').find('a') #Mencari informasi penjual pada tag div dan class css-1rn0irl dan menyimpan pada variable seller_info

                    #Memanggil fungsi mengambil Text (get_text()) dan menambahkan serta menyimpan pada variable list
                    if title and price and 'seller_info':
                        titles.append(title.get_text().strip('\n'))
                        prices.append(price.get_text())
                        # links.append(link.get('href'))

                    else:
                        continue
                    
                    if sold_info:
                        sold_infos.append(sold_info.get_text())
                    else:
                        sold_infos.append(None)

                    if rating:
                        ratings.append(rating.find('span').get_text())
                    else:
                        ratings.append(None)

                    if seller_info:
                        sellers.append(seller_info.find_all('span')[0].get_text())
                        locations.append(seller_info.find_all('span')[1].get_text())
                    else:
                        sellers.append(None)
                        locations.append(None)
                    
            dataframe_json = pd.read_json(soup.find_all("script", {"type":"application/ld+json"})[0].get_text())
            for i in dict(dataframe_json['itemListElement']):
                links.append('https://www.blibli.com'+str(dict(dataframe_json['itemListElement'])[i]['item']['url']))
        except Exception as e:
            print(f"An error occurred while scraping Blibli: {str(e)}")
            # You can add more error handling or logging here as needed.
            driver.quit()
            # driver = webdriver.Chrome()
            # driver.maximize_window()
            time.sleep(5)  # Wait for 60 seconds before retrying (adjust as needed)
        else:
            break    
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
    #Save raw Data
    data = data.apply(lambda x: x.str.replace('\n', ''))
    data.to_csv('BliBliMas_raw.csv',index=False)
    

def clean_blibli():
    data = pd.read_csv('BliBliMas_raw.csv')
    
    data['product_name'] = data['product_name'].str.strip()
    #Mengubah Kolom "Price" menjadi tipe integer
    data['price'] = data['price'].str.replace("Mulai  ","").str.replace("Rp","").str.replace(".","").astype(int)

    #Mengubah Kolom "Number Sold" menjadi tipe numerik dan extract value
    data['number_sold'] = data['number_sold'].str.replace("Terjual","").str.replace("+","").str.replace("rb","000").str.replace(",","").str.replace(" ","")
    data['number_sold'].fillna('0', inplace=True)
    data['number_sold'] = data['number_sold'].astype(int)


    #Mengisi missing value pada Rating dengan rata rata seluruh rating
    data['rating'].fillna('0', inplace=True)
    #change "rating" column to float datatype
    data['rating']= data['rating'].str.replace(",",".")
    data['rating']= data['rating'].astype(float)
    #drop any missing value
    data = data.dropna()

    # Nama file CSV yang akan diperiksa
    early_file_name = 'BlibliMas_clean_early.csv'
    latest_file_name = 'BlibliMas_clean_latest.csv'

    # Mengecek apakah file CSV sudah ada
    
    if os.path.exists(latest_file_name):
        old_data = pd.read_csv(latest_file_name)
        old_data = old_data.drop_duplicates()
        old_data.to_csv(early_file_name, index=False)
        new_data = pd.read_csv(early_file_name)
        new_data = pd.concat([old_data, data])
        new_data = new_data.drop_duplicates()
        new_data.to_csv(latest_file_name, index=False)
    else:
        data.to_csv(latest_file_name, index=False)

if __name__ == '__main__':
    webscrap_blibli()
    clean_blibli()