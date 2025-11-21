import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- 1. CONFIGURATION & UI POLISH ---
st.set_page_config(page_title="Zero", page_icon="⭕", layout="centered")

# Advanced CSS for the "Premium App" feel
st.markdown("""
    <style>
    /* 1. Main Background & Text */
    .stApp { 
        background-color: #000000; 
        color: #ffffff; 
    }
    
    /* 2. Hide Streamlit default elements */
    header {visibility: hidden;}
    .stApp > footer {display: none;}
    
    /* 3. Button Styling - Gradient & Roundness */
    .stButton button {
        width: 100%;
        height: 3.2rem;
        border-radius: 12px;
        font-weight: 600;
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #333;
        transition: all 0.2s;
    }
    .stButton button:hover {
        border-color: #00FF94; /* Neon Green Hover */
        color: #00FF94;
    }
    
    /* 4. Metric Styling */
    [data-testid="stMetricValue"] { 
        font-size: 2.5rem !important; 
        font-family: 'Helvetica Neue', sans-serif;
        color: #00FF94; /* Neon Green for numbers */
    }
    [data-testid="stMetricLabel"] {
        color: #888;
        font-size: 0.9rem;
    }
    
    /* 5. Spacing adjustments for mobile */
    div.block-container { padding-top: 1rem; padding-bottom: 4rem; }
    
    /* 6. Remove white background from charts if any */
    .js-plotly-plot .plotly .main-svg {
        background: rgba(0,0,0,0) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE FUNCTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

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
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        conn.update(worksheet="Logs", data=updated_df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def update_settings(quit_date, cost, cigs):
    try:
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

# Load Settings
df_set = get_data("Settings")
if not df_set.empty:
    my_settings = dict(zip(df_set['Key'], df_set['Value']))
else:
    my_settings = {}

days, money, avoided, hours, q_date_obj, s_cost, s_daily = get_progress(my_settings)

# CLEANER TABS
tab1, tab2, tab3, tab4 = st.tabs([" 🔥 ZERO ", " 🛡️ FIGHT ", " 📈 DATA ", " ⚙️ SET "])

# === TAB 1: DASHBOARD ===
with tab1:
    st.caption("CURRENT STREAK")
    st.title("Zero.")
    
    # Card-like layout using containers
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Days Free", f"{days}")
        c2.metric("Saved", f"${money:,.0f}")
        
    with st.container(border=True):
        col_a, col_b = st.columns([3, 1])
        col_a.metric("Cigarettes Avoided", f"{int(avoided)}")
        col_b.markdown("# 💀") # Big icon

    st.divider()
    
    # Health Logic
    st.subheader("🧬 Biological Status")
    
    if hours < 24:
        prog = hours / 24
        stage = "CO Flushing Out"
        icon = "🩸"
    elif hours < 72:
        prog = (hours - 24) / 48
        stage = "Nicotine Leaving Body"
        icon = "🧠"
    elif hours < 336: 
        prog = (hours - 72) / (336 - 72)
        stage = "Lung Function +10%"
        icon = "🫁"
    else:
        prog = 1.0
        stage = "Long-term Recovery"
        icon = "❤️"
        
    st.write(f"**{icon} {stage}**")
    st.progress(min(prog, 1.0))

# === TAB 2: THE FIGHT ===
with tab2:
    st.header("Combat Zone")
    
    # RED EMERGENCY CONTAINER
    with st.container(border=True):
        st.markdown("### 🚨 Panic Button")
        if st.toggle("I need help right now"):
            st.warning("STOP. Do not smoke.")
            
            task = random.choice([
                "💧 Chug a glass of ice water", 
                "🏃‍♂️ Do 10 Pushups NOW", 
                "🌬️ Box Breathe (4s in, 4s hold, 4s out)", 
                "🚶 Walk around the block"
            ])
            st.info(f"**MISSION:** {task}")
            
            if st.button("Start 3-Min Focus Timer"):
                bar = st.progress(0, text="Stay strong...")
                for i in range(100):
                    time.sleep(0.05) 
                    bar.progress(i+1)
                st.balloons()
                st.success("Urge defeated.")

    st.write("") # Spacer
    
    # LOGGING FORM CONTAINER
    with st.container(border=True):
        st.markdown("### 📝 Log a Craving")
        with st.form("craving_log"):
            intensity = st.slider("Urge Intensity", 1, 10, 5)
            
            c1, c2 = st.columns(2)
            trigger = c1.selectbox("Trigger", ["Stress", "Boredom", "Meal", "Social", "Alcohol", "Waking Up"])
            location = c2.selectbox("Location", ["Home", "Work", "Outside", "Car/Transit"])
            
            action = st.text_input("Alternative Action", placeholder="e.g. Drank Water")
            resisted = st.checkbox("I Resisted ✅", value=True)
            
            if st.form_submit_button("Save Entry"):
                res_str = "TRUE" if resisted else "FALSE"
                if write_log(intensity, trigger, action, res_str, location):
                    st.toast("Entry Saved!", icon="💾")
                    time.sleep(1)
                    st.rerun()

# === TAB 3: STATS ===
with tab3:
    st.header("Analytics")
    logs = get_data("Logs")
    
    if not logs.empty and "Trigger" in logs.columns:
        
        with st.container(border=True):
            st.caption("WHAT TRIGGERS YOU?")
            counts = logs["Trigger"].value_counts().reset_index()
            counts.columns = ["Trigger", "Count"]
            
            # Dark Mode Chart
            fig = px.bar(counts, x="Trigger", y="Count", color="Trigger")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with st.container(border=True):
            st.caption("RECENT LOGS")
            st.dataframe(logs.tail(3)[['Timestamp', 'Trigger', 'Resisted']], use_container_width=True, hide_index=True)
            
    else:
        st.info("Log your first craving to unlock charts.")

# === TAB 4: SETUP ===
with tab4:
    st.header("Calibration")
    with st.container(border=True):
        with st.form("setup_form"):
            d_date = st.text_input("Quit Date (YYYY-MM-DD)", str(q_date_obj.date()))
            d_cost = st.number_input("Cost per Pack ($)", value=s_cost)
            d_cigs = st.number_input("Cigs per Day", value=s_daily)
            
            if st.form_submit_button("Update Baseline"):
                if update_settings(d_date, d_cost, d_cigs):
                    st.toast("Settings Updated", icon="✅")
                    time.sleep(1)
                    st.rerun()
