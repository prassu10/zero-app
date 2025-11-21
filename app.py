import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Connection Test")

try:
    # 1. Connect to the secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Try to read the 'Logs' tab
    st.write("Attempting to read Google Sheet...")
    data = conn.read(worksheet="Logs")
    
    # 3. Success Message
    st.success("✅ SUCCESS! We are connected.")
    st.write("Here is the raw data from your sheet:")
    st.dataframe(data)

except Exception as e:
    # 4. Failure Message
    st.error(f"❌ Connection Failed. Error: {e}")
