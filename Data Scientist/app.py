import pandas as pd
import re
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

# Load your data (replace 'silver_clean.csv' with your actual file)
silver_df = pd.read_csv('silver_clean_processed.csv')

# Function to extract category from input description
def extract_category(item):
    coin_name_list = ['coin', 'koin', 'coins']
    bar_name_list = ['batang', 'batangan', 'bar', 'bars']

    output = ''

    for _name in coin_name_list:
        if _name in item:
            output += 'coin'
            break

    for _name in bar_name_list:
        if _name in item:
            if not output:
                output += 'bar'
            else:
                output += ' & bar'
            break

    if output != 'coin':
        output = 'bar'

    return output

# Function to get weight from user input
def get_weight(input):
    input_weight = re.findall(rf"\b\d+(?:\.\d+)*\s*(?:{'oz|ounce|ons'})\b", input)
    input_weight = [x.replace('oz', '') for x in input_weight]
    input_weight = [x.replace('ounce', '') for x in input_weight]
    input_weight = [x.replace('ons', '') for x in input_weight]
    input_weight = [x.strip() for x in input_weight]
    input_weight = " ".join(set(input_weight))
    if input_weight:
        input_weight = float(input_weight)
    else:
        input_weight = 0.0
    return input_weight

# Function to calculate recommendation score
def calculate_recommendation_score(input_category_df, input_weight, input_description):
    input_category_df['number_sold_normalized'] = input_category_df['number_sold'] / input_category_df['number_sold'].max() 
    input_category_df['rating'] = input_category_df['rating'].str.replace(',', '').astype(float)
    scaler = MinMaxScaler()
    input_category_df['price_per_oz_normalized'] = scaler.fit_transform(input_category_df[['price_per_oz']])

    def get_jaccard_distance(str1, str2):
        a = set(str1.split())
        b = set(str2.split())
        c = a.intersection(b)
        return float(len(c)) / (len(a) + len(b) - len(c))

    input_category_df['jaccard_distance'] = input_category_df['product_name_lower'].apply(lambda x: get_jaccard_distance(x, input_description.lower()))

    scaler.fit(input_category_df[['price_per_oz']])
    input_category_df['price_distance'] = 1 - scaler.transform(input_category_df[['price_per_oz']])


    input_category_df['recommendation_score'] = \
        (0.3 * (input_category_df['jaccard_distance'] / 1)) + \
        (0.2 * input_category_df['number_sold_normalized']) + \
        (0.2 * (input_category_df['rating'] / 5)) + \
        (0.3 * input_category_df['price_distance'])

    return input_category_df

# Streamlit app
def main():
    st.set_page_config(
        page_title="Silver Product Recommendation",
        page_icon=":bar_chart:",
        layout="wide"
    )

    st.title('Silver Product Recommendation')

    # Input box for user to enter product description
    input_description = st.text_input('Enter the product name:')

    # Check if there is user input
    if input_description:
        # Extract category from input description
        input_category = extract_category(input_description.lower())

        # Filter based on input_category
        input_category_df = silver_df[silver_df['category'] == input_category]

        # Get weight from input description
        input_weight = get_weight(input_description)

        # Check if the 'weight' column is present in the DataFrame
        if 'weight' in input_category_df.columns:
            # Filter based on input_weight
            input_weight_df = input_category_df[input_category_df['weight'] == input_weight]
            if input_weight_df.empty:
                input_weight_df = input_category_df
        else:
            st.warning("The 'weight' column is not present in the DataFrame.")

        # Calculate recommendation score
        input_weight_df = calculate_recommendation_score(input_weight_df, input_weight, input_description)

        # Display the top recommendations
        st.subheader('Top Recommendations:')
        st.table(
            input_weight_df[['product_name_lower', 'number_sold', 'rating', 'price', 'price_per_oz', 'recommendation_score',
                            'link']].sort_values(by=['recommendation_score'], ascending=False)[:10])

if __name__ == '__main__':
    main()