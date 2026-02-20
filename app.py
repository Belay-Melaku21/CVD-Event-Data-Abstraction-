import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# የገጽ መዋቅር
st.set_page_config(page_title="CVD Data Abstraction", layout="wide")

st.title("Cardiovascular Disease (CVD) Event Data Abstraction Checklist")
st.markdown("Study Title: **Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients...**")

# ከGoogle Sheet ጋር ግንኙነት መፍጠር
conn = st.connection("gsheets", type=GSheetsConnection)

# ቅጹን መጀመር
with st.form(key="cvd_form"):
    # SECTION 1: IDENTIFICATION
    st.header("SECTION 1: IDENTIFICATION & TRACKING")
    col1, col2 = st.columns(2)
    with col1:
        health_center = st.text_input("1.1. Health Center Name")
        mrn = st.text_input("1.2. Patient Medical Record Number (MRN)")
    with col2:
        date_extraction = st.date_input("1.3. Date of Data Extraction", datetime.now())
        date_enrollment = st.date_input("1.4. Date of Enrollment (Baseline Visit)")
    cohort_status = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

    st.divider()

    # SECTION 2: SOCIO-DEMOGRAPHIC
    st.header("SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
    col3, col4 = st.columns(2)
    with col3:
        age = st.number_input("2.1. Age (in years)", min_value=0, max_value=120)
        sex = st.selectbox("2.2. Sex", ["Male", "Female"])
        residence = st.selectbox("2.3. Residence", ["Urban", "Rural"])
    with col4:
        edu = st.selectbox("2.4. Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        occ = st.selectbox("2.5. Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = st.selectbox("2.6. Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

    st.divider()

    # SECTION 3: LIFESTYLE
    st.header("SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS")
    col5, col6 = st.columns(2)
    with col5:
        tobacco = st.selectbox("3.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        alcohol = st.selectbox("3.2. Alcohol Consumption", ["Non-user", "Current User"])
        khat = st.selectbox("3.3. Khat Chewing", ["Never", "Current User", "History of regular use"])
    with col6:
        physical = st.radio("3.4. Physical Activity (≥30 min/day, 5 days/week)", ["Physically Active", "Inactive"])
        salt = st.radio("3.5. Salt Intake", ["High (Adds salt to food)", "Normal/Low"])

    st.divider()

    # SECTION 4: CLINICAL MEASUREMENTS
    st.header("SECTION 4: CLINICAL & PHYSIOLOGICAL MEASUREMENTS")
    sbp = st.number_input("4.1. SBP (mmHg)", min_value=50, max_value=250)
    dbp = st.number_input("4.1. DBP (mmHg)", min_value=30, max_value=150)
    htn_stage = st.selectbox("4.2. Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
    
    col7, col8 = st.columns(2)
    with col7:
        weight = st.number_input("4.3. Weight (kg)", min_value=20.0, max_value=200.0)
        height = st.number_input("4.3. Height (cm)", min_value=50.0, max_value=250.0)
    
    # BMI calculation logic
    if height > 0:
        bmi_calc = round(weight / ((height/100)**2), 2)
        st.info(f"Calculated BMI: {bmi_calc}")
    
    bmi_cat = st.selectbox("4.4. BMI Category", ["Underweight (<18.5)", "Normal", "Overweight (25-29.9)", "Obese (≥30)"])
    htn_duration = st.text_input("4.5. Duration of HTN (months/years)")
    family_hx = st.radio("4.6. Family History of CVD/HTN", ["Yes", "No"])

    st.divider()

    # SECTION 5 & 6: BIOCHEMICAL & TREATMENT
    st.header("SECTION 5 & 6: BIOCHEMICAL & TREATMENT")
    dm = st.radio("5.1. Diabetes Mellitus (DM)", ["Yes", "No"])
    ckd = st.radio("5.2. Chronic Kidney Disease (CKD)", ["Yes", "No"])
    med_type = st.selectbox("6.1. Type of Antihypertensive Meds", ["Monotherapy", "Dual Therapy", "Polytherapy"])
    adherence = st.radio("6.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

    st.divider()

    # SECTION 7: OUTCOME
    st.header("SECTION 7: OUTCOME & SURVIVAL DATA")
    cvd_event = st.radio("7.1. CVD Event Occurred?", ["Yes", "No"])
    event_type = st.multiselect("7.2. Type of CVD Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
    date_event = st.date_input("7.3. Date of CVD Event", value=None)
    censoring = st.selectbox("7.4. Censoring Details", ["Lost to Follow-up", "Died (Non-CVD cause)", "Study ended without event", "N/A"])
    date_last_followup = st.date_input("7.5. Date of Last Follow-up/Censoring")

    # Submit Button
    submit_button = st.form_submit_button(label="Save Data to Google Sheets")

    if submit_button:
        # መረጃውን ወደ DataFrame መቀየር
        new_data = pd.DataFrame([{
            "Health Center": health_center,
            "MRN": mrn,
            "Date Extracted": str(date_extraction),
            "Age": age,
            "Sex": sex,
            "BMI": bmi_calc if height > 0 else 0,
            "CVD Event": cvd_event,
            "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        # ወደ Google Sheet መላክ
        try:
            existing_data = conn.read(worksheet="Sheet1", usecols=list(range(len(new_data.columns))))
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("መረጃው በትክክል ተመዝግቧል! (Data saved successfully!)")
        except Exception as e:
            st.error(f"Error: {e}")
