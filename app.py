import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. AUTHENTICATION FUNCTION DEFINITION ---
# This MUST be defined before it is called
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Secure Data Access")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and password == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        return False
    return True

# --- 2. APP INITIALIZATION ---
st.set_page_config(page_title="CVD Data Abstraction", layout="wide")

if check_password():
    # PROFESSIONAL INTRODUCTION
    st.title("Cardiovascular Disease (CVD) Event Data Abstraction Checklist")
    st.markdown("### Study Title: Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients")
    
    st.info("""
    **Notice to Data Collector:** Please handle all patient information with strict confidentiality. 
    Ensure all data extracted is accurate and reflects the medical records precisely. 
    Thank you for your professional contribution to this research.
    """)

    # Google Sheets Connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_form", clear_on_submit=True):
        # SECTION 1: IDENTIFICATION
        st.subheader("SECTION 1: IDENTIFICATION & TRACKING")
        c1, c2 = st.columns(2)
        hc_name = c1.selectbox("1.1 Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = c2.text_input("1.2 Patient Medical Record Number (MRN)")
        extract_date = c1.date_input("1.3 Date of Data Extraction")
        enroll_date = c2.date_input("1.4 Date of Enrollment (Baseline Visit)")
        cohort = st.radio("1.5 Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"], horizontal=True)

        # SECTION 2: SOCIO-DEMOGRAPHIC
        st.subheader("SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
        c3, c4 = st.columns(2)
        age = c3.number_input("2.1 Age (in years)", min_value=0)
        sex = c4.selectbox("2.2 Sex", ["Male", "Female"])
        residence = c3.selectbox("2.3 Residence", ["Urban", "Rural"])
        edu = c4.selectbox("2.4 Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        occ = c3.selectbox("2.5 Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = c4.selectbox("2.6 Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

        # SECTION 3: LIFESTYLE
        st.subheader("SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS")
        tobacco = st.selectbox("3.1 Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        alcohol = st.selectbox("3.2 Alcohol Consumption", ["Non-user", "Current User"])
        
        # SMART LOGIC: Alcohol
        avg_drinks = 0
        if alcohol == "Current User":
            avg_drinks = st.number_input("Average standard drinks/day", min_value=1)
        
        khat = st.selectbox("3.3 Khat Chewing", ["Never", "Current User", "History of regular use"])
        physical = st.radio("3.4 Physical Activity", ["Physically Active (≥30 min/day)", "Inactive"], horizontal=True)
        salt = st.radio("3.5 Salt Intake", ["High (Adds salt to food)", "Normal/Low"], horizontal=True)

        # SECTION 4: CLINICAL (Smart BMI and BP)
        st.subheader("SECTION 4: CLINICAL & PHYSIOLOGICAL MEASUREMENTS")
        c5, c6 = st.columns(2)
        sbp = c5.number_input("SBP (mmHg)", min_value=50)
        dbp = c6.number_input("DBP (mmHg)", min_value=30)
        
        # SMART LOGIC: BP Stage
        bp_stage = "Normal"
        if sbp >= 160 or dbp >= 110: bp_stage = "Stage 3/4"
        elif sbp >= 160 or dbp >= 100: bp_stage = "Stage 2"
        elif sbp >= 140 or dbp >= 90: bp_stage = "Stage 1"
        elif sbp > 120 or dbp > 80: bp_stage = "Pre-HTN"
        st.write(f"**Automatic Hypertension Stage:** {bp_stage}")

        weight = c5.number_input("Weight (kg)", min_value=1.0)
        height = c6.number_input("Height (cm)", min_value=1.0)
        
        # SMART LOGIC: BMI Calculation
        bmi = 0.0
        bmi_cat = "N/A"
        if weight > 0 and height > 0:
            bmi = round(weight / ((height/100)**2), 2)
            if bmi < 18.5: bmi_cat = "Underweight"
            elif 18.5 <= bmi < 25: bmi_cat = "Normal"
            elif 25 <= bmi < 30: bmi_cat = "Overweight"
            else: bmi_cat = "Obese"
        st.write(f"**Calculated BMI:** {bmi} | **Category:** {bmi_cat}")

        # SMART LOGIC: Duration
        target_date = datetime(2025, 11, 9).date()
        duration = (target_date.year - enroll_date.year) * 12 + (target_date.month - enroll_date.month)
        st.write(f"**HTN Duration (to Nov 9, 2025):** {duration} months")

        # OUTCOME DATA
        st.subheader("SECTION 7: OUTCOME & SURVIVAL DATA")
        cvd_event = st.radio("7.1 CVD Event Occurred?", ["No", "Yes"], horizontal=True)
        
        # SMART LOGIC: Event Type
        event_type = "N/A"
        event_date = "N/A"
        if cvd_event == "Yes":
            event_type = st.selectbox("7.2 Type of CVD Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
            event_date = st.date_input("7.3 Date of CVD Event")

        submit = st.form_submit_button("Submit Data")

        if submit:
            # Prepare data row
            new_entry = pd.DataFrame([{
                "HC Name": hc_name, "MRN": mrn, "Date": str(extract_date), "Enroll": str(enroll_date),
                "Cohort": cohort, "Age": age, "Sex": sex, "Residence": residence, "Education": edu,
                "Occupation": occ, "Marital": marital, "Tobacco": tobacco, "Alcohol": alcohol,
                "Drinks": avg_drinks, "Khat": khat, "Active": physical, "Salt": salt,
                "SBP": sbp, "DBP": dbp, "BP Stage": bp_stage, "BMI": bmi, "BMI Cat": bmi_cat,
                "Duration": duration, "CVD Event": cvd_event, "Event Type": event_type, "Event Date": str(event_date)
            }])
            
            # Submit to GSheets
            conn.create(data=new_entry)
            st.success("Record Saved Successfully! Thank you for your contribution.")
            st.balloons()
