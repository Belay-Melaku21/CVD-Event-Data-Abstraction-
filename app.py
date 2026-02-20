import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG & STYLE ---
st.set_page_config(page_title="CVD Data Abstraction", layout="centered")

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Secure Access")
    user_input = st.text_input("User Name")
    pass_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if user_input == "Belay Melaku" and pass_input == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# --- APP INTERFACE ---
st.title("Cardiovascular Disease (CVD) Data Abstraction")

# Professional Introduction [cite: 9, 10, 15]
st.markdown("""
### Confidential Data Entry Portal
**Study:** *Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients on Follow-Up at Health Centers in Mehal Amhara Saynt District.*

> **Professional Notice:** Please ensure all data points are extracted with clinical precision. The integrity of this research depends on your accurate input. All patient information must be handled with strict confidentiality. 
> 
> *Thank you for your valued contribution to this study.*
""")

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("cvd_form", clear_on_submit=True):
    # SECTION 1: IDENTIFICATION [cite: 16, 17, 18, 20, 21]
    st.header("Section 1: Identification")
    hc_name = st.selectbox("1.1 Health Center", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
    mrn = st.text_input("1.2 Patient Medical Record Number (MRN)")
    date_ext = st.date_input("1.3 Date of Extraction")
    date_enroll = st.date_input("1.4 Date of Enrollment")
    cohort = st.radio("1.5 Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

    # SECTION 2: ELIGIBILITY [cite: 22, 23, 24, 25]
    st.header("Section 2: Eligibility")
    age_elig = st.radio("Is Age ≥ 18 years?", ["Yes", "No"])
    pre_cvd = st.radio("Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["Yes", "No"])
    preg_htn = st.radio("Pregnancy-induced Hypertension?", ["Yes", "No"])

    # STOP LOGIC: If any eligibility fails [cite: 23, 24, 25]
    if age_elig == "No" or pre_cvd == "Yes" or preg_htn == "Yes":
        st.error("⛔ Patient is INELIGIBLE. Do not proceed.")
        eligible = False
    else:
        eligible = True

    if eligible:
        # SECTION 3: SOCIO-DEMOGRAPHIC [cite: 26, 27, 28, 31]
        st.header("Section 3: Socio-Demographic")
        age = st.number_input("3.1 Age (years)", min_value=18)
        sex = st.selectbox("3.2 Sex", ["Male", "Female"])
        occ = st.selectbox("3.5 Occupation", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        occ_spec = st.text_input("If Other, specify:") if occ == "Other" else ""

        # SECTION 4: LIFESTYLE (Conditional Logic) [cite: 33, 35, 37]
        st.header("Section 4: Lifestyle")
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["Non-user", "Current User"])
        # Conditional Skip [cite: 7, 35]
        drinks = 0
        if alcohol == "Current User":
            drinks = st.number_input("Average standard drinks/day", min_value=0)
        
        phys_act = st.radio("4.4 Physical Activity", ["Physically Active", "Inactive"])

        # SECTION 5: CLINICAL & BMI [cite: 40, 42, 43, 8]
        st.header("Section 5: Clinical Measurements")
        sbp = st.number_input("SBP (mmHg)")
        dbp = st.number_input("DBP (mmHg)")
        weight = st.number_input("Weight (kg)", min_value=1.0)
        height = st.number_input("Height (cm)", min_value=1.0)
        
        # Auto BMI Calculation [cite: 8, 42, 43]
        bmi = round(weight / ((height/100)**2), 2)
        if bmi < 18.5: bmi_cat = "Underweight"
        elif 18.5 <= bmi < 25: bmi_cat = "Normal"
        elif 25 <= bmi < 30: bmi_cat = "Overweight"
        else: bmi_cat = "Obese"
        st.info(f"Calculated BMI: {bmi} ({bmi_cat})")

        # SECTION 8: OUTCOME [cite: 56, 57, 58, 59]
        st.header("Section 8: Outcome")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["Yes", "No"])
        # Conditional Skip [cite: 7, 57]
        cvd_type = ""
        cvd_date = None
        if cvd_event == "Yes":
            cvd_type = st.selectbox("8.2 Type of Event", ["Stroke", "MI", "Heart Failure"])
            cvd_date = st.date_input("8.3 Date of Event")

    submit_button = st.form_submit_button("Submit Data to Google Sheets")

if submit_button:
    if eligible:
        # Create Dataframe for Google Sheets [cite: 4, 5, 11]
        data = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "HC Name": hc_name, "MRN": mrn, "Age": age, "Sex": sex, 
            "Alcohol": alcohol, "Drinks/Day": drinks, "BMI": bmi, "Category": bmi_cat,
            "CVD Event": cvd_event, "Event Type": cvd_type, "Event Date": str(cvd_date)
        }])
        
        # Append logic
        existing_data = conn.read(worksheet="Sheet1")
        updated_data = pd.concat([existing_data, data], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_data)
        
        st.success("✅ Data successfully recorded! The form has been reset for the next patient.")
        st.balloons()
