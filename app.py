import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- 1. CONFIGURATION & MOBILE STYLING ---
st.set_page_config(page_title="Zero", page_icon="⭕", layout="centered")

# This CSS makes the app look like a native iOS app AND hides the header
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    
    /* HIDE STREAMLIT HEADER & FOOTER */
    header {visibility: hidden;}
    .stApp > footer {display: none;}
    
    /* Big, thumb-friendly buttons */
    .stButton button {
        width: 100%;
        height: 3.5rem;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
    }
    
    /* Hide top padding so it fits iPhone screen better */
    div.block-container { padding-top: 0.5rem; padding-bottom: 3rem; }
    
    /* Make metrics large and readable */
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; }
    </style>
""", unsafe_allow_html=True)
# --- 2. DATABASE FUNCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    # ttl=0 ensures we don't use old cached data
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

def write_log(intensity, trigger, action, resisted, location):
    try:
        df = get_data("Logs")
        # Create the new row
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Intensity": intensity,
            "Trigger": trigger,
            "Action": action,
            "Resisted": resisted,
            "Location": location
        }])
        # Combine with old data
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        conn.update(worksheet="Logs", data=updated_df)
        st.cache_data.clear() # Force the app to reload data
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def update_settings(quit_date, cost, cigs):
    try:
        # Create a simple table for settings
        new_settings = pd.DataFrame([
            {"Key": "quit_date", "Value": str(quit_date)},
            {"Key": "cost_per_pack", "Value": str(cost)},
            {"Key": "cigs_per_day", "Value": str(cigs)}
        ])
        conn.update(worksheet="Settings", data=new_settings)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Settings Error: {e}")
        return False

# --- 3. CALCULATIONS ---
def get_progress(settings_dict):
    # Default values if settings are empty
    q_date = settings_dict.get('quit_date', '2024-01-01')
    cost = float(settings_dict.get('cost_per_pack', 12.0))
    daily = float(settings_dict.get('cigs_per_day', 15.0))
    
    try:
        quit_dt = datetime.strptime(q_date, "%Y-%m-%d")
    except:
        quit_dt = datetime(2024, 1, 1)

    delta = datetime.now() - quit_dt
    days = delta.days
    money = days * (cost / 20 * daily)
    avoided = days * daily
    hours = delta.total_seconds() / 3600
    return days, money, avoided, hours, quit_dt, cost, daily

# --- 4. APP INTERFACE ---

# Load Settings First
df_set = get_data("Settings")
if not df_set.empty:
    my_settings = dict(zip(df_set['Key'], df_set['Value']))
else:
    my_settings = {}

days, money, avoided, hours, q_date_obj, s_cost, s_daily = get_progress(my_settings)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Zero", "🛡️ Fight", "📊 Stats", "⚙️ Setup"])

# === TAB 1: DASHBOARD ===
with tab1:
    st.title("Zero.")
    
    # Main Stats
    c1, c2 = st.columns(2)
    c1.metric("Days Free", f"{days}")
    c2.metric("Saved", f"${money:,.0f}")
    st.metric("Cigarettes Avoided", f"{int(avoided)} 💀")

    st.divider()
    
    # Health Logic
    st.subheader("❤️ Healing Process")
    if hours < 24:
        prog = hours / 24
        stage = "Carbon Monoxide flushing out"
    elif hours < 72:
        prog = (hours - 24) / 48
        stage = "Nicotine leaving body"
    elif hours < 336: # 2 weeks
        prog = (hours - 72) / (336 - 72)
        stage = "Lung function improving"
    else:
        prog = 1.0
        stage = "Long-term recovery"
        
    st.write(f"**Stage:** {stage}")
    st.progress(min(prog, 1.0))

# === TAB 2: THE FIGHT ===
with tab2:
    st.header("Combat Urges")
    
    # PANIC BUTTON
    if st.toggle("🚨 Emergency Mode"):
        st.warning("STOP. Don't do it.")
        
        task = random.choice(["Drink water", "10 Pushups", "Deep Breaths", "Walk Outside"])
        st.info(f"**Your Mission:** {task}")
        
        if st.button("Start 3-Min Timer"):
            bar = st.progress(0, text="Breathe in...")
            for i in range(100):
                time.sleep(0.05) # Fast for demo (Change to 1.8 for real time)
                bar.progress(i+1)
            st.balloons()
            st.success("You won this round.")

    st.divider()
    
    # LOGGING FORM
    with st.form("craving_log"):
        st.write("Log to track your triggers.")
        intensity = st.slider("Intensity", 1, 10, 5)
        trigger = st.selectbox("Trigger", ["Stress", "Boredom", "Meal", "Social", "Alcohol", "Waking Up"])
        action = st.text_input("What did you do?", "Resisted")
        resisted = st.checkbox("I Resisted ✅", value=True)
        location = st.selectbox("Location", ["Home", "Work", "Outside", "Car/Transit"])
        
        if st.form_submit_button("Save Log"):
            res_str = "TRUE" if resisted else "FALSE"
            if write_log(intensity, trigger, action, res_str, location):
                st.success("Saved!")
                time.sleep(1)
                st.rerun()

# === TAB 3: STATS ===
with tab3:
    st.header("Your Data")
    logs = get_data("Logs")
    
    if not logs.empty and "Trigger" in logs.columns:
        # Chart 1: Triggers
        counts = logs["Trigger"].value_counts().reset_index()
        counts.columns = ["Trigger", "Count"]
        fig = px.bar(counts, x="Trigger", y="Count", color="Trigger")
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent History
        st.write("Recent Logs:")
        st.dataframe(logs.tail(3), use_container_width=True)
    else:
        st.info("Log your first craving in the 'Fight' tab to see charts here.")

# === TAB 4: SETUP ===
with tab4:
    st.header("Settings")
    with st.form("setup_form"):
        d_date = st.text_input("Quit Date (YYYY-MM-DD)", str(q_date_obj.date()))
        d_cost = st.number_input("Cost per Pack ($)", value=s_cost)
        d_cigs = st.number_input("Cigs per Day", value=s_daily)
        
        if st.form_submit_button("Save Settings"):
            if update_settings(d_date, d_cost, d_cigs):
                st.success("Updated! Refreshing...")
                time.sleep(1)
                st.rerun()
