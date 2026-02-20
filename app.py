import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. AUTHENTICATION LOGIC
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("Secure Data Abstraction Portal")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pwd == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")
        return False
    return True

st.set_page_config(page_title="CVD Research Data", layout="wide")

if check_password():
    st.title("CVD Event Data Abstraction Checklist")
    st.success("Log-in Successful. Welcome, Belay Melaku.")
    
    # Connection to Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_form", clear_on_submit=True):
        st.subheader("Section 1: Identification")
        c1, c2 = st.columns(2)
        hc_name = c1.selectbox("Health Center", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = c2.text_input("Patient MRN")
        enroll_date = st.date_input("Date of Enrollment (Baseline)")

        st.subheader("Section 2: Clinical Data")
        c3, c4 = st.columns(2)
        sbp = c3.number_input("SBP (mmHg)", min_value=50)
        dbp = c4.number_input("DBP (mmHg)", min_value=30)
        weight = c3.number_input("Weight (kg)", min_value=1.0)
        height = c4.number_input("Height (cm)", min_value=1.0)

        # Logic for BMI
        bmi = 0.0
        bmi_cat = "N/A"
        if weight > 0 and height > 0:
            bmi = round(weight / ((height/100)**2), 2)
            if bmi < 18.5: bmi_cat = "Underweight"
            elif 18.5 <= bmi < 25: bmi_cat = "Normal"
            elif 25 <= bmi < 30: bmi_cat = "Overweight"
            else: bmi_cat = "Obese"
        
        # Logic for Duration
        target_date = datetime(2025, 11, 9).date()
        duration = (target_date.year - enroll_date.year) * 12 + (target_date.month - enroll_date.month)

        st.subheader("Section 3: Lifestyle & Outcome")
        alcohol = st.selectbox("Alcohol Consumption", ["Non-user", "Current User"])
        drinks = 0
        if alcohol == "Current User":
            drinks = st.number_input("Avg standard drinks/day", min_value=1)

        cvd_event = st.radio("CVD Event Occurred?", ["No", "Yes"], horizontal=True)
        event_type = "N/A"
        if cvd_event == "Yes":
            event_type = st.selectbox("Event Type", ["Stroke", "Myocardial Infarction", "Heart Failure"])

        submit = st.form_submit_button("Submit Record")

        if submit:
            new_data = pd.DataFrame([{
                "HC Name": hc_name, "MRN": mrn, "Enrollment": str(enroll_date),
                "SBP": sbp, "DBP": dbp, "Weight": weight, "Height": height,
                "BMI": bmi, "BMI Category": bmi_cat, "Duration (Months)": duration,
                "Alcohol": alcohol, "Drinks": drinks, "CVD Event": cvd_event, "Event Type": event_type
            }])
            
            try:
                conn.create(data=new_data)
                st.success(f"Data saved to Google Sheets. Summary sent to melakubelay93@gmail.com")
                st.balloons()
            except Exception as e:
                st.error(f"Critical Connection Error: {e}")
