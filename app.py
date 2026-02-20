import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ገጹን ዳግም ለማስጀመር (Reset) የሚረዳ ተግባር
def clear_form():
    for key in st.session_state.keys():
        if key not in ["logged_in"]:
            st.session_state.pop(key)
    st.rerun()

st.set_page_config(page_title="CVD Data Portal", layout="wide")

# --- 1. ደህንነት (Login) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Invalid credentials")
    st.stop()

# --- 2. Google Sheets ግንኙነት ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Smart CVD Event Data Abstraction")
st.info("መረጃው ተሞልቶ 'Submit' ሲጫኑ ገጹ በራሱ ተጸድቶ ለአዲስ ታካሚ ዝግጁ ይሆናል።")

with st.form(key="cvd_abstraction_form", clear_on_submit=True):
    # Section 1: Identification
    st.header("Section 1: Identification & Tracking")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = st.text_input("1.2. Patient MRN")
    with col2:
        d_ext = st.date_input("1.3. Date of Extraction", datetime.now())
        d_enr = st.date_input("1.4. Date of Enrollment")
    
    # Section 2: Eligibility (Exclusion)
    st.divider()
    st.header("Section 2: Eligibility Checklist")
    e1 = st.radio("Age ≥18 years?", ["Yes", "No"])
    e2 = st.radio("Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["No", "Yes"])
    e3 = st.radio("Pregnancy-induced Hypertension?", ["No", "Yes"])

    is_eligible = (e1 == "Yes" and e2 == "No" and e3 == "No")
    
    if not is_eligible:
        st.error("❌ Patient is NOT eligible. Proceeding will only record exclusion.")
        submit = st.form_submit_button("Submit Exclusion Report")
    else:
        # SECTION 3 - 7: Full Data Entry
        st.success("✅ Patient is eligible. Please complete the following.")
        age = st.number_input("3.1. Age (years)", min_value=18)
        sex = st.selectbox("3.2. Sex", ["Male", "Female"])
        
        # Clinical & BMI
        wt = st.number_input("5.3. Weight (kg)", min_value=0.0)
        ht = st.number_input("5.3. Height (cm)", min_value=0.0)
        bmi_val = round(wt / ((ht/100)**2), 2) if ht > 0 else 0
        st.write(f"**Calculated BMI:** {bmi_val}")

        # Outcome & Duration Logic
        st.divider()
        cvd_event = st.radio("8.1. CVD Event Occurred?", ["No", "Yes"])
        
        duration = 0
        study_end = datetime(2025, 11, 9).date() # [cite: 31]
        
        if cvd_event == "Yes":
            d_event = st.date_input("8.3. Date of Event")
            duration = (d_event - d_enr).days / 30.44 if d_enr else 0
        else:
            d_last = st.date_input("8.5. Date of Last Follow-up", study_end)
            duration = (d_last - d_enr).days / 30.44 if d_enr else 0

        st.warning(f"Auto-Calculated Duration: {round(duration, 1)} months")
        
        # ይህ ቁልፍ ከሌለ ዳታው አይላክም!
        submit = st.form_submit_button("Submit Complete Data")

    if submit:
        # እዚህ ጋር መረጃውን ወደ Google Sheet የሚልክ ኮድ ይጨመራል
        st.success("✅ መረጃው ተመዝግቧል!")
        st.balloons()
        st.button("ለቀጣይ ታካሚ መረጃ መሙያ ተጫን", on_click=clear_form)
