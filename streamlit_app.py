# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# App title and UI
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write('Choose the fruits you want in your custom Smoothie!')

name_on_order = st.text_input('Name')
st.write(f"The name on your smoothie will be {name_on_order}")

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Show fruit options
st.dataframe(pd_df)

# Fruit selection UI
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# If fruits selected, process selection
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            response.raise_for_status()
            st.dataframe(response.json(), use_container_width=True)
        except requests.RequestException as e:
            st.error(f"Failed to fetch nutrition data for {fruit_chosen}: {e}")

    # Insert into database using parameterized query (safe)
    if st.button('Submit Order'):
        session.sql("""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (:1, :2)
        """).bind((ingredients_string, name_on_order)).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
