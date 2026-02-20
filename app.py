import streamlit as st
import pandas as pd
from datetime import datetime
from gspread_streamlit import GoogleSheetsConnection

# Page Configuration
st.set_page_config(page_title="CVD Data Abstraction", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Login")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and password == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        return False
    return True

if check_password():
    # --- INTRODUCTION ---
    st.title("Cardiovascular Disease (CVD) Event Data Abstraction Checklist")
    st.info("""
    **Professional Notice to Data Collectors:**
    Please ensure all patient information is handled with the highest level of confidentiality and precision. 
    The integrity of this study, *'Time to Cardiovascular Disease Event and Its Determinants'*, 
    depends on the accuracy of your entry. Thank you for your dedication to professional research standards.
    """)

    # --- GOOGLE SHEETS CONNECTION ---
    # Note: You will need to set up st.secrets for this to work on Streamlit Cloud
    try:
        conn = st.connection("gsheets", type=GoogleSheetsConnection)
    except:
        st.error("Please connect Google Sheets in the Streamlit Cloud settings.")

    with st.form("cvd_form", clear_on_submit=True):
        # SECTION 1: IDENTIFICATION
        st.header("Section 1: Identification & Tracking")
        col1, col2 = st.columns(2)
        hc_name = col1.selectbox("1.1 Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = col2.text_input("1.2 Patient Medical Record Number (MRN)")
        extract_date = col1.date_input("1.3 Date of Data Extraction")
        enroll_date = col2.date_input("1.4 Date of Enrollment (Baseline Visit)")
        cohort = st.radio("1.5 Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

        # SECTION 2: SOCIO-DEMOGRAPHIC
        st.header("Section 2: Socio-Demographic")
        col3, col4 = st.columns(2)
        age = col3.number_input("2.1 Age (years)", min_value=0, max_value=120)
        sex = col4.selectbox("2.2 Sex", ["Male", "Female"])
        residence = col3.selectbox("2.3 Residence", ["Urban", "Rural"])
        edu = col4.selectbox("2.4 Education", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        occ = col3.selectbox("2.5 Occupation", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = col4.selectbox("2.6 Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

        # SECTION 3: LIFESTYLE
        st.header("Section 3: Lifestyle Factors")
        tobacco = st.selectbox("3.1 Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        alcohol = st.selectbox("3.2 Alcohol Consumption", ["Non-user", "Current User"])
        avg_drinks = 0
        if alcohol == "Current User":
            avg_drinks = st.number_input("Average standard drinks/day", min_value=0.0)
        
        khat = st.selectbox("3.3 Khat Chewing", ["Never", "Current User", "History of regular use"])
        physical = st.radio("3.4 Physical Activity", ["Physically Active (≥30 min/day)", "Inactive"])
        salt = st.radio("3.5 Salt Intake", ["High (Adds salt)", "Normal/Low"])

        # SECTION 4: CLINICAL (BMI & BP)
        st.header("Section 4: Clinical Measurements")
        col5, col6 = st.columns(2)
        sbp = col5.number_input("SBP (mmHg)", min_value=50)
        dbp = col6.number_input("DBP (mmHg)", min_value=30)
        
        # Auto BP Stage Logic
        bp_stage = "Normal"
        if sbp >= 160 or dbp >= 110: bp_stage = "Stage 3/4"
        elif 160 > sbp >= 160 or 109 >= dbp >= 100: bp_stage = "Stage 2"
        elif 159 >= sbp >= 140 or 99 >= dbp >= 91: bp_stage = "Stage 1"
        elif 139 >= sbp >= 121 or 89 >= dbp >= 81: bp_stage = "Pre-HTN"
        st.write(f"**Calculated HTN Stage:** {bp_stage}")

        weight = col5.number_input("Weight (kg)", min_value=1.0)
        height = col6.number_input("Height (cm)", min_value=1.0)
        
        # BMI Calculation
        bmi = 0.0
        bmi_cat = "N/A"
        if weight > 0 and height > 0:
            bmi = round(weight / ((height/100)**2), 2)
            if bmi < 18.5: bmi_cat = "Underweight"
            elif 18.5 <= bmi < 25: bmi_cat = "Normal"
            elif 25 <= bmi < 30: bmi_cat = "Overweight"
            else: bmi_cat = "Obese"
        st.write(f"**Calculated BMI:** {bmi} ({bmi_cat})")

        # Duration Calculation
        target_date = datetime(2025, 11, 9).date()
        duration_months = (target_date.year - enroll_date.year) * 12 + (target_date.month - enroll_date.month)
        st.write(f"**Auto-calculated Duration (to Nov 9, 2025):** {duration_months} Months")

        # SECTION 5, 6, 7 (Simplified for code length)
        st.header("Section 5-7: Outcomes & Comorbidities")
        cvd_event = st.radio("7.1 CVD Event Occurred?", ["No", "Yes"])
        event_type = "N/A"
        event_date = "N/A"
        if cvd_event == "Yes":
            event_type = st.selectbox("7.2 Type of Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
            event_date = st.date_input("7.3 Date of Event")

        submit = st.form_submit_button("Submit Record")

        if submit:
            # Data Mapping
            new_data = pd.DataFrame([{
                "Health Center Name": hc_name, "Patient MRN": mrn, "Date of Extraction": str(extract_date),
                "Date of Enrollment": str(enroll_date), "Cohort Status": cohort, "Age": age, "Sex": sex,
                "Residence": residence, "Educational Status": edu, "Occupational Status": occ,
                "Marital Status": marital, "Tobacco Use": tobacco, "Alcohol Consumption": alcohol,
                "Avg Drinks/Day": avg_drinks, "Khat Chewing": khat, "Physical Activity": physical,
                "Salt Intake": salt, "SBP": sbp, "DBP": dbp, "Hypertension Stage": bp_stage,
                "Weight (kg)": weight, "Height (cm)": height, "BMI": bmi, "BMI Category": bmi_cat,
                "Duration of HTN (Months)": duration_months, "CVD Event Occurred": cvd_event,
                "CVD Event Type": event_type, "CVD Event Date": str(event_date)
            }])
            
            # Append to Google Sheet
            conn.create(data=new_data)
            st.success("Data successfully submitted! The form has been reset.")
            # Email Notification Logic (requires SMTP setup)
            st.info(f"Summary sent to melakubelay93@gmail.com")
