import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zero",
                   page_icon="⭕️",
                   layout="centerted")

st.title("Zero.")
st.header("Welcome to yput fresh start.")
st.write("If you can see this on your iPhone, the app is live!")

# A dummy button to test interaction
if st.button('Click Me'):
    st.balloons()