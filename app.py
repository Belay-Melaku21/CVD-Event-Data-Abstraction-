import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart CVD Data Entry", layout="wide")

# --- Authentication ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 CVD Research Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Smart CVD Event Data Abstraction Form")
st.write("**Study Title:** Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients [cite: 2]")

# Introduction and Notice
st.info("**Data Integrity & Confidentiality:** Please ensure all data is accurate and directly from medical records. Your diligence is key to this research[cite: 1].")
st.success("Thank you for your professional contribution to this study!")

with st.form(key="smart_cvd_form"):
    # SECTION 1: IDENTIFICATION
    st.header("Section 1: Identification & Tracking [cite: 3]")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"]) [cite: 4]
        mrn = st.text_input("1.2. Patient MRN") [cite: 5]
    with col2:
        d_ext = st.date_input("1.3. Date of Extraction", datetime.now()) [cite: 6]
        d_enr = st.date_input("1.4. Date of Enrollment (Baseline)") [cite: 7]
    cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"]) [cite: 8]

    # SECTION 2: ELIGIBILITY CHECK (Exclusion Logic)
    st.divider()
    st.header("Section 2: Eligibility Checklist [cite: 9]")
    st.warning("If any 'Yes' is selected below, do not proceed with data entry.")
    age_less_18 = st.radio("2.1. Age <18 years?", ["No", "Yes"]) [cite: 10]
    pre_cvd = st.radio("2.2. Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["No", "Yes"]) [cite: 11]
    preg_htn = st.radio("2.3. Pregnancy-induced Hypertension?", ["No", "Yes"]) [cite: 12]

    # SECTION 3-7: Visible only if Eligible
    is_eligible = (age_less_18 == "No" and pre_cvd == "No" and preg_htn == "No")
    
    if not is_eligible:
        st.error("❌ Patient is NOT eligible according to the exclusion criteria[cite: 9, 10, 11, 12].")
        submitted = st.form_submit_button("Submit Exclusion Report")
    else:
        st.success("✅ Patient is eligible. Please complete the following sections[cite: 13, 20, 26].")
        
        # SECTION 3: SOCIO-DEMOGRAPHIC
        st.header("Section 3: Socio-Demographic Characteristics [cite: 13]")
        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("3.1. Age (years)", min_value=18, max_value=120) [cite: 14]
            sex = st.selectbox("3.2. Sex", ["Male", "Female"]) [cite: 15]
            res = st.selectbox("3.3. Residence", ["Urban", "Rural"]) [cite: 16]
        with col4:
            edu = st.selectbox("3.4. Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"]) [cite: 17]
            occ = st.selectbox("3.5. Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"]) [cite: 18]
            marital = st.selectbox("3.6. Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"]) [cite: 19]

        # SECTION 4: LIFESTYLE
        st.divider()
        st.header("Section 4: Lifestyle & Behavioral Factors [cite: 20]")
        col5, col6 = st.columns(2)
        with col5:
            tobacco = st.selectbox("4.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"]) [cite: 21]
            alcohol = st.selectbox("4.2. Alcohol Consumption", ["Non-user", "Current User"]) [cite: 22]
            # IF Logic for Alcohol Quantity
            alc_qty = 0.0
            if alcohol == "Current User":
                alc_qty = st.number_input("Average standard drinks/day", min_value=0.0) [cite: 22]
        with col6:
            khat = st.selectbox("4.3. Khat Chewing", ["Never", "Current User", "History of regular use"]) [cite: 23]
            phys = st.radio("4.4. Physical Activity (≥30 min/day)", ["Physically Active", "Inactive"]) [cite: 24]
            salt = st.radio("4.5. Salt Intake", ["High (Adds salt)", "Normal/Low"]) [cite: 25]

        # SECTION 5: CLINICAL (Smart BMI & Auto Duration)
        st.divider()
        st.header("Section 5: Clinical & Physiological Measurements [cite: 26]")
        col7, col8 = st.columns(2)
        with col7:
            sbp = st.number_input("5.1. Baseline SBP (mmHg)", min_value=0) [cite: 27]
            dbp = st.number_input("5.1. Baseline DBP (mmHg)", min_value=0) [cite: 27]
            wt = st.number_input("5.3. Weight (kg)", min_value=0.0) [cite: 29]
            ht = st.number_input("5.3. Height (cm)", min_value=0.0) [cite: 29]
        with col8:
            # Automatic BMI Calculation [cite: 29]
            bmi_val = 0.0
            bmi_cat = "N/A"
            if ht > 0:
                bmi_val = round(wt / ((ht/100)**2), 2) [cite: 29]
                if bmi_val < 18.5: bmi_cat = "Underweight"
                elif 18.5 <= bmi_val < 25: bmi_cat = "Normal"
                elif 25 <= bmi_val < 30: bmi_cat = "Overweight"
                else: bmi_cat = "Obese" [cite: 30]
            st.info(f"Calculated BMI: {bmi_val} ({bmi_cat}) ")
            
            htn_stage = st.selectbox("5.2. Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"]) [cite: 28]
            fam_hx = st.radio("5.6. Family History of CVD/HTN", ["Yes", "No"]) [cite: 32]

        # SECTION 6: BIOCHEMICAL
        st.divider()
        st.header("Section 6: Biochemical & Comorbidity [cite: 33]")
        col9, col10 = st.columns(2)
        with col9:
            dm = st.radio("6.1. Diabetes Mellitus (DM)", ["No", "Yes"]) [cite: 34]
            ckd = st.radio("6.2. Chronic Kidney Disease (CKD)", ["No", "Yes"]) [cite: 35]
            prot = st.selectbox("6.3. Proteinuria", ["Negative", "Positive"]) [cite: 36]
            # IF Logic for Proteinuria detail
            prot_detail = "N/A"
            if prot == "Positive":
                prot_detail = st.selectbox("Proteinuria Level", ["+", "++", "+++", "++++"]) [cite: 36]
        with col10:
            chol = st.number_input("6.4. Total Cholesterol (mg/dL)", min_value=0.0) [cite: 37]
            compl = st.multiselect("6.5. Baseline Complications", ["None", "Prior Stroke", "Prior Cardiac issues"]) [cite: 38]

        # SECTION 7: TREATMENT
        st.divider()
        st.header("Section 7: Treatment & Management [cite: 39]")
        tx_type = st.selectbox("7.1. Type of Antihypertensive Meds", ["Monotherapy", "Dual Therapy", "Polytherapy"]) [cite: 40]
        tx_class = st.multiselect("7.2. Specific Class", ["ACEi/ARB", "CCB", "Diuretics", "Beta-Blockers"]) [cite: 41]
        adh = st.radio("7.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"]) [cite: 42]

        # SECTION 8: OUTCOME (Smart Logic)
        st.divider()
        st.header("Section 8: Outcome & Survival Data [cite: 43]")
        cvd_event = st.radio("8.1. CVD Event Occurred?", ["No", "Yes"]) [cite: 44]
        
        event_type = "N/A"
        d_event = None
        censor_detail = "N/A"
        d_last = None
        duration_val = 0
        
        if cvd_event == "Yes":
            col11, col12 = st.columns(2)
            with col11:
                event_type = st.selectbox("8.2. Type of CVD Event", ["Stroke", "MI", "Heart Failure"]) [cite: 45]
            with col12:
                d_event = st.date_input("8.3. Date of CVD Event") [cite: 46]
            # Auto duration: Date of Event - Enrollment 
            if d_event and d_enr:
                duration_val = (d_event - d_enr).days / 30.44 # in months
        else:
            col13, col14 = st.columns(2)
            with col13:
                censor_detail = st.selectbox("8.4. Censoring Details", ["Study ended without event", "Lost to Follow-up", "Died (Non-CVD)"]) [cite: 47]
            with col14:
                # Default follow-up date 
                study_end = datetime(2025, 11, 9).date()
                d_last = st.date_input("8.5. Date of Last Follow-up", study_end) [cite: 48]
            # Auto duration: Last Follow-up/Nov 9 - Enrollment 
            if d_last and d_enr:
                duration_val = (d_last - d_enr).days / 30.44

        st.warning(f"5.5. Auto-Calculated HTN Duration: {round(duration_val, 1)} months ")

        submitted = st.form_submit_button("Submit Complete Data")

    if submitted:
        new_row = {
            "HC_Name": h_center, "MRN": mrn, "Enrollment_Date": str(d_enr),
            "Eligible": is_eligible, "BMI": bmi_val, "BMI_Category": bmi_cat,
            "HTN_Duration_Months": round(duration_val, 1),
            "CVD_Event": cvd_event, "Event_Type": event_type,
            "Follow_up_Date": str(d_event if cvd_event == "Yes" else d_last)
        }
        # Connection logic...
        st.success("Data processed and ready for storage! [cite: 1]")
