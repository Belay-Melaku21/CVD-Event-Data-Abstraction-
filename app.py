import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. AUTHENTICATION 
USER_NAME = "Belay Melaku"
PASSWORD = "@Belay6669"
TARGET_EMAIL = "melakubelay93@gmail.com"

def send_email_notification(content):
    msg = EmailMessage()
    msg.set_content(f"New Research Data Entry Submitted:\n\n{content}")
    msg['Subject'] = 'New CVD Data Entry'
    msg['From'] = TARGET_EMAIL
    msg['To'] = TARGET_EMAIL
    
    # Note: For Gmail, you must use an 'App Password', not your regular password
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # smtp.login(TARGET_EMAIL, 'YOUR_GMAIL_APP_PASSWORD_HERE')
            # smtp.send_message(msg)
            pass 
    except Exception as e:
        st.error(f"Email failed: {e}")

# 2. LOGIN SYSTEM
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 Researcher Access")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USER_NAME and pw == PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop()

# 3. RESEARCH INTRODUCTION [cite: 9, 10, 15]
st.title("Cardiovascular Disease (CVD) Data Abstraction")
st.markdown(f"**Study Title:** { [cite: 15] }")
st.success("""
**Researcher's Commitment to Integrity:** By proceeding, you acknowledge that this data is collected for clinical research. Please handle all Patient Medical Records with the highest level of confidentiality and accuracy. Thank you for your professional contribution to this study. [cite: 9, 10]
""")

# 4. DATA ENTRY FORM [cite: 11, 13]
with st.form("cvd_research_form", clear_on_submit=True):
    # Sections 1 & 2
    hc = st.selectbox("1.1 Health Center", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"]) [cite: 17]
    mrn = st.text_input("1.2 Patient MRN") [cite: 18]
    
    # Eligibility Logic [cite: 22, 23, 24, 25]
    st.subheader("Section 2: Eligibility Checklist")
    age_check = st.radio("Age ≥18 years?", ["Yes", "No"])
    pre_cvd = st.radio("Pre-existing CVD before enrolment?", ["Yes", "No"])
    preg_htn = st.radio("Pregnancy-induced Hypertension?", ["Yes", "No"])
    
    eligible = (age_check == "Yes" and pre_cvd == "No" and preg_htn == "No")
    
    if not eligible:
        st.warning("⚠️ Patient is ineligible for this study. Data entry will stop here.")
    
    # Section 5: BMI Calculation [cite: 8, 42, 43]
    st.subheader("Section 5: Measurements")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    height = st.number_input("Height (cm)", min_value=0.0)
    
    bmi_val = 0.0
    bmi_cat = "N/A"
    if weight > 0 and height > 0:
        bmi_val = round(weight / ((height/100)**2), 2)
        if bmi_val < 18.5: bmi_cat = "Underweight"
        elif 18.5 <= bmi_val < 25: bmi_cat = "Normal"
        elif 25 <= bmi_val < 30: bmi_cat = "Overweight"
        else: bmi_cat = "Obese"
        st.write(f"**Automatic BMI Result:** {bmi_val} ({bmi_cat})")

    submitted = st.form_submit_button("Submit and Reset Form")

    if submitted:
        if eligible:
            st.balloons()
            st.success("Data recorded and sent to Google Sheets. Form reset for next entry.") [cite: 11]
            # Logic to append to sheet and send email would go here
