import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# -------------------------
# Secure Login
# -------------------------
def login():
    st.title("🔒 Secure Login")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and password == "@Belay6669":
            st.session_state["authenticated"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# -------------------------
# Google Sheets Connection
# -------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(st.secrets["sheet_url"]).sheet1

# -------------------------
# Disclaimer
# -------------------------
st.markdown("### 📜 Disclaimer")
st.info("All data collected is confidential. Patient names are never recorded. "
        "Only MRN and Study IDs are used to ensure anonymity.")

# -------------------------
# Data Collection Form
# -------------------------
with st.form("data_form", clear_on_submit=True):
    study_id = st.text_input("Study ID")
    mrn = st.text_input("Patient MRN")
    age = st.number_input("Age", min_value=18, max_value=120)
    sex = st.selectbox("Sex", ["Male", "Female"])
    residence = st.selectbox("Residence", ["Urban", "Rural"])
    
    # Lifestyle factors
    tobacco = st.selectbox("Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
    alcohol = st.selectbox("Alcohol Consumption", ["Non-user", "Current User"])
    drinks_per_day = None
    if alcohol == "Current User":
        drinks_per_day = st.number_input("Average drinks/day", min_value=0.0)
    
    khat = st.selectbox("Khat Chewing", ["Never", "Current User", "History of regular use"])
    physical_activity = st.selectbox("Physical Activity", ["Active", "Inactive"])
    salt_intake = st.selectbox("Salt Intake", ["High", "Normal/Low"])
    
    # Clinical measurements
    weight = st.number_input("Weight (kg)", min_value=1.0)
    height = st.number_input("Height (cm)", min_value=50.0)
    bmi = round(weight / ((height/100)**2), 2) if height > 0 else None
    bmi_category = None
    if bmi:
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
        st.write(f"**BMI:** {bmi} ({bmi_category})")
    
    # Outcome
    cvd_event = st.selectbox("CVD Event Occurred?", ["Yes", "No"])
    cvd_type = None
    if cvd_event == "Yes":
        cvd_type = st.selectbox("Type of CVD Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
    
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Save to Google Sheet
        row = [study_id, mrn, age, sex, residence, tobacco, alcohol, drinks_per_day,
               khat, physical_activity, salt_intake, weight, height, bmi, bmi_category,
               cvd_event, cvd_type]
        sheet.append_row(row)

        # Email summary
        summary = f"""
        Study ID: {study_id}
        MRN: {mrn}
        Age: {age}, Sex: {sex}, Residence: {residence}
        Tobacco: {tobacco}, Alcohol: {alcohol}, Drinks/day: {drinks_per_day}
        Khat: {khat}, Physical Activity: {physical_activity}, Salt Intake: {salt_intake}
        Weight: {weight} kg, Height: {height} cm, BMI: {bmi} ({bmi_category})
        CVD Event: {cvd_event}, Type: {cvd_type}
        """
        msg = MIMEText(summary)
        msg["Subject"] = "New CVD Data Submission"
        msg["From"] = "noreply@datacollection.com"
        msg["To"] = "melakubelay93@gmail.com"

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                # Use app password for Gmail
                server.login("your-email@gmail.com", "your-app-password")
                server.send_message(msg)
        except Exception as e:
            st.error(f"Email failed: {e}")

        st.success("✅ Data submitted successfully! Thank you.")
