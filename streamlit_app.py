# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Establish a Streamlit connection to Snowflake 
cnx = st.connection("snowflake")
session = cnx.session()

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write('Choose the fruits you want in your custom Smoothie!')

# Name Input
name_on_order = st.text_input('Name')
st.write(f"The name on your smoothie will be {name_on_order}") 

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)  # Optional display for debugging

# Use .multiselect with a list of fruit names
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get SEARCH_ON value from the dataframe
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display Nutrition Info header
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Call the SmoothieFroot API
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(api_url)

        if response.status_code == 200:
            try:
                st.dataframe(data=response.json(), use_container_width=True)
            except ValueError:
                st.warning("API did not return JSON data.")
        else:
            st.error(f"API request failed for {fruit_chosen} (status code {response.status_code})")

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Submit order button
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
