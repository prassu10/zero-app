import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- 1. CONFIG & MOBILE STYLING ---
st.set_page_config(page_title="Zero", page_icon="⭕", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* Make buttons big and thumb-friendly */
    .stButton button {
        width: 100%;
        height: 3.5rem;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
    }
    /* Adjust spacing for mobile screens */
    div.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
# This connects to your "secrets.toml" automatically
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    # ttl=0 means "don't cache the data forever, fetch it fresh"
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except Exception:
        return pd.DataFrame() # Return empty if sheet is empty/error

def write_log(intensity, trigger, action, resisted, location):
    try:
        df = get_data("Logs")
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Intensity": intensity,
            "Trigger": trigger,
            "Action": action,
            "Resisted": resisted,
            "Location": location
        }])
        # If df is empty, just use new_entry, otherwise append
        updated_df = new_entry if df.empty else pd.concat([df, new_entry], ignore_index=True)
        conn.update(worksheet="Logs", data=updated_df)
        st.cache_data.clear() # Reset cache so we see the new log immediately
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

# --- 3. CALCULATIONS ---
def calculate_stats(quit_date_str, cost, daily_cigs):
    try:
        quit_date = datetime.strptime(quit_date_str, "%Y-%m-%d")
    except:
        quit_date = datetime(2024, 1, 1) # Fallback
        
    now = datetime.now()
    delta = now - quit_date
    
    days_free = delta.days
    money_saved = days_free * (cost / 20 * daily_cigs)
    cigs_avoided = days_free * daily_cigs
    hours_free = delta.total_seconds() / 3600
    
    return days_free, money_saved, cigs_avoided, hours_free

def get_dopamine_task():
    tasks = [
        "🥤 Chug a glass of cold water.",
        "🏃 15 Jumping Jacks. Go.",
        "🌬️ Box Breathe (4-4-4-4).",
        "💪 10 Pushups right now.",
        "🧼 Splash cold water on your face."
    ]
    return random.choice(tasks)

# --- 4. MAIN APP ---

# FETCH SETTINGS
try:
    settings_df = get_data("Settings")
    if not settings_df.empty:
        # Assuming columns are Key, Value
        settings = dict(zip(settings_df['Key'], settings_df['Value']))
        QUIT_DATE = str(settings.get('quit_date', '2024-01-01'))
        COST_PACK = float(settings.get('cost_per_pack', 12.0))
        CIGS_DAY = float(settings.get('cigs_per_day', 15.0))
    else:
        raise ValueError("Empty Settings")
except:
    # Defaults if sheet is empty
    QUIT_DATE = '2024-01-01'
    COST_PACK = 12.0
    CIGS_DAY = 15.0

days, money, avoided, hours, = calculate_stats(QUIT_DATE, COST_PACK, CIGS_DAY)

# UI TABS
tab1, tab2, tab3 = st.tabs(["🏠 Zero", "⚡ Fight", "📊 Data"])

# === TAB 1: DASHBOARD ===
with tab1:
    st.title("Zero.")
    
    c1, c2 = st.columns(2)
    c1.metric("Days Free", f"{days}")
    c2.metric("Saved", f"${money:,.0f}")
    st.metric("Avoided", f"{int(avoided)} 🚬")
    
    st.divider()
    st.caption("Current Health Status")
    
    # Simple Health Bar Logic
    if hours < 24:
        msg, val = "Clearing CO from blood", hours/24
    elif hours < 72:
        msg, val = "Nicotine exiting body", (hours-24)/48
    elif hours < 336:
        msg, val = "Lungs repairing", (hours-72)/(336-72)
    else:
        msg, val = "Long-term Healing", 1.0
        
    st.write(f"**{msg}**")
    st.progress(min(val, 1.0))

# === TAB 2: THE FIGHT (Logger) ===
with tab2:
    # SOS BUTTON
    if st.toggle("🚨 I need help (Panic Mode)"):
        st.info(get_dopamine_task())
        if st.button("Start 3-Min Timer"):
            with st.empty():
                for i in range(100):
                    st.progress(i + 1, text="Just breathe... this will pass.")
                    time.sleep(0.05) # Fast for demo, set 1.8 for real time
            st.balloons()
            st.success("You did it.")
            
    st.divider()
    
    # LOGGING
    st.subheader("Log Activity")
    with st.form("log"):
        intensity = st.slider("Urge (1-10)", 1, 10, 5)
        trigger = st.selectbox("Trigger", ["Stress", "Boredom", "Meal", "Alcohol", "Waking Up", "Social"])
        action = st.text_input("Action Taken", "Drank water")
        resisted = st.checkbox("I RESISTED ✅", value=True)
        location = st.selectbox("Location", ["Home", "Work", "Outside", "Car"])
        
        if st.form_submit_button("Save Log"):
            success = write_log(intensity, trigger, action, str(resisted), location)
            if success:
                st.success("Saved.")
                time.sleep(1)
                st.rerun()

# === TAB 3: DATA ===
with tab3:
    st.header("Analysis")
    logs = get_data("Logs")
    
    if not logs.empty and "Trigger" in logs.columns:
        st.caption("Top Triggers")
        # Count occurrences
        counts = logs["Trigger"].value_counts().reset_index()
        counts.columns = ["Trigger", "Count"]
        fig = px.bar(counts, x="Trigger", y="Count", color="Trigger")
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("Raw Logs")
        st.dataframe(logs.tail(5), use_container_width=True)
    else:
        st.info("Log your first craving to see charts!")

    # SETTINGS UPDATE
    with st.expander("⚙️ Update Settings"):
        with st.form("set_up"):
            d_date = st.text_input("Quit Date (YYYY-MM-DD)", QUIT_DATE)
            d_cost = st.number_input("Cost ($)", value=COST_PACK)
            d_cigs = st.number_input("Cigs/Day", value=CIGS_DAY)
            if st.form_submit_button("Save Settings"):
                # Creating a new DF to overwrite settings
                new_settings = pd.DataFrame([
                    {"Key": "quit_date", "Value": d_date},
                    {"Key": "cost_per_pack", "Value": d_cost},
                    {"Key": "cigs_per_day", "Value": d_cigs}
                ])
                conn.update(worksheet="Settings", data=new_settings)
                st.cache_data.clear()
                st.success("Updated! Refreshing...")
                time.sleep(1)
                st.rerun()

