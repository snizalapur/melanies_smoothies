# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Example Streamlit App :balloon:")
st.write(
    "Chose the Fruits you want in your custo smoothie"
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your smoothie will be',name_on_order)


# title = st.text_input('Moviee Title','Life of Brian')
# st.write('The currentn movie title is',title)

conn = st.connection("snowflake")
session = conn.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()
                                                                      
ingredients_list = st.multiselect(
    'Chose upto 5 ingredients :'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

time_to_insert = st.button("Submit Order")
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")

import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
fv_dt = st.dataframe(data=fruityvice_response.json(),use_container_width=True)

if ingredients_list:
        ingredients_string = ''
        for furit_chosen in ingredients_list:   
            ingredients_string += furit_chosen + ' '
            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.subheader(furit_chosen + 'Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fv_dt = st.dataframe(data=fruityvice_response.json(),use_container_width=True)

#st.write(ingredients_string)
