# Import python packages
import streamlit as st
import requests  # <-- Newly added
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want to have in your Smoothie!"""
)

# SmoothieFroot API Call
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Display the API response
st.subheader("SmoothieFroot Watermelon Info:")
if smoothiefroot_response.status_code == 200:
    try:
        st.json(smoothiefroot_response.json())  # Better display if it's JSON
    except ValueError:
        st.text(smoothiefroot_response.text)
else:
    st.error("Failed to fetch data from SmoothieFroot API.")

# Snowflake connection and data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name in your Smoothie will be:", name_on_order)

# Multiselect input
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: ', my_dataframe, max_selections=5
)

# If user selected ingredients
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
