import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="CVD Data Abstraction", layout="wide")

# User Credentials [cite: 3]
USER_NAME = "Belay Melaku"
PASSWORD = "@Belay6669"

def login():
    st.sidebar.title("Researcher Login")
    user = st.sidebar.text_input("User Name")
    pw = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user == USER_NAME and pw == PASSWORD:
            st.session_state["logged_in"] = True
            st.sidebar.success("Logged In!")
        else:
            st.sidebar.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    login()

if st.session_state["logged_in"]:
    # Header and Professional Introduction [cite: 9, 10, 15]
    st.title("🩺 Cardiovascular Disease (CVD) Data Abstraction")
    st.info("""
    **Professional Disclosure:** This application is designed for the study: *'Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients'*. 
    Please ensure all data is entered with the highest level of precision and confidentiality. 
    We sincerely appreciate your dedication to maintaining the integrity of this clinical research. [cite: 10]
    """)

    # Google Sheets Connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_form", clear_on_submit=True): # clear_on_submit handles [cite: 11]
        
        # SECTION 1: IDENTIFICATION [cite: 16, 17]
        st.subheader("Section 1: Identification & Tracking")
        hc_name = st.selectbox("1.1 Health Center", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = st.text_input("1.2 Patient Medical Record Number (MRN)")
        col1, col2 = st.columns(2)
        date_ext = col1.date_input("1.3 Date of Data Extraction")
        date_enroll = col2.date_input("1.4 Date of Enrollment")
        cohort = st.radio("1.5 Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

        # SECTION 2: ELIGIBILITY [cite: 22, 23, 24, 25]
        st.subheader("Section 2: Eligibility Checklist")
        age_elig = st.radio("Is Age ≥ 18 years?", ["Yes", "No"])
        pre_cvd = st.radio("Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["Yes", "No"])
        preg_htn = st.radio("Pregnancy-induced Hypertension?", ["Yes", "No"])

        if age_elig == "No" or pre_cvd == "Yes" or preg_htn == "Yes":
            st.warning("⚠️ Patient is ineligible. Please do not proceed with data entry.")
            submit = st.form_submit_button("Submit Eligibility Status Only")
        else:
            # SECTION 3: SOCIO-DEMOGRAPHIC [cite: 26-32]
            st.subheader("Section 3: Socio-Demographic")
            age = st.number_input("3.1 Age (years)", min_value=18, max_value=120)
            sex = st.selectbox("3.2 Sex", ["Male", "Female"])
            residence = st.selectbox("3.3 Residence", ["Urban", "Rural"])
            edu = st.selectbox("3.4 Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"])
            occ = st.selectbox("3.5 Occupation", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
            occ_other = ""
            if occ == "Other":
                occ_other = st.text_input("Specify Occupation")
            marital = st.selectbox("3.6 Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

            # SECTION 4: LIFESTYLE [cite: 33-38]
            st.subheader("Section 4: Lifestyle Factors")
            tobacco = st.selectbox("4.1 Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
            alcohol = st.selectbox("4.2 Alcohol Consumption", ["Non-user", "Current User"])
            drinks = 0
            if alcohol == "Current User": # Conditional logic [cite: 7]
                drinks = st.number_input("Average standard drinks/day", min_value=0.0)
            khat = st.selectbox("4.3 Khat Chewing", ["Never", "Current User", "History of regular use"])
            phys = st.selectbox("4.4 Physical Activity", ["Physically Active", "Inactive"])
            salt = st.selectbox("4.5 Salt Intake", ["High", "Normal/Low"])

            # SECTION 5: CLINICAL [cite: 39-45]
            st.subheader("Section 5: Clinical Measurements")
            sbp = st.number_input("SBP (mmHg)")
            dbp = st.number_input("DBP (mmHg)")
            htn_stage = st.selectbox("5.2 Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
            
            weight = st.number_input("Weight (kg)", min_value=1.0)
            height = st.number_input("Height (cm)", min_value=1.0)
            
            # BMI Calculation [cite: 8]
            bmi = 0.0
            bmi_cat = "N/A"
            if weight > 0 and height > 0:
                bmi = round(weight / ((height/100)**2), 2)
                if bmi < 18.5: bmi_cat = "Underweight"
                elif 18.5 <= bmi < 25: bmi_cat = "Normal"
                elif 25 <= bmi < 30: bmi_cat = "Overweight"
                else: bmi_cat = "Obese"
                st.write(f"**Calculated BMI:** {bmi} ({bmi_cat})")

            htn_dur = st.text_input("5.5 Duration of HTN (months/years)")
            fam_hx = st.radio("5.6 Family History of CVD/HTN", ["Yes", "No"])

            # SECTION 6: BIOCHEMICAL [cite: 46-51]
            st.subheader("Section 6: Biochemical Profile")
            dm = st.radio("6.1 Diabetes Mellitus?", ["Yes", "No"])
            dm_date = st.date_input("DM Date of Enrollment") if dm == "Yes" else None
            ckd = st.radio("6.2 Chronic Kidney Disease?", ["Yes", "No"])
            ckd_date = st.date_input("CKD Date of Diagnosis") if ckd == "Yes" else None
            prot = st.radio("6.3 Proteinuria", ["Positive", "Negative"])
            prot_lvl = st.selectbox("Level", ["+", "++", "+++", "++++"]) if prot == "Positive" else "N/A"
            chol = st.number_input("6.4 Total Cholesterol (mg/dL)", value=0)
            comp = st.selectbox("6.5 Baseline Complications", ["None", "Prior Stroke", "Prior Cardiac issues"])

            # SECTION 7: TREATMENT [cite: 52-55]
            st.subheader("Section 7: Treatment")
            tx_type = st.selectbox("7.1 Meds Type", ["Monotherapy", "Dual Therapy", "Polytherapy"])
            tx_class = st.multiselect("7.2 Specific Class", ["ACEi/ARB", "CCB", "Diuretics", "Beta-Blockers"])
            adherence = st.radio("7.3 Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

            # SECTION 8: OUTCOME [cite: 56-61]
            st.subheader("Section 8: Outcome Data")
            cvd_event = st.radio("8.1 CVD Event Occurred?", ["Yes", "No"])
            cvd_type, cvd_date, censor, last_date = "N/A", None, "N/A", None
            
            if cvd_event == "Yes":
                cvd_type = st.selectbox("8.2 Type of Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
                cvd_date = st.date_input("8.3 Date of Event")
            else:
                censor = st.selectbox("8.4 Censoring Details", ["Lost to Follow-up", "Died (Non-CVD)", "Study ended"])
                last_date = st.date_input("8.5 Date of Last Follow-up")

            submit = st.form_submit_button("Submit Final Data")

        if submit:
            # Data Preparation for Sheet
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Health Center": hc_name, "MRN": mrn, "Extraction Date": str(date_ext),
                "Enrollment Date": str(date_enroll), "Cohort Status": cohort, "Age": age if 'age' in locals() else 0,
                "Sex": sex if 'sex' in locals() else "", "BMI": bmi if 'bmi' in locals() else 0,
                "BMI Category": bmi_cat if 'bmi_cat' in locals() else "",
                "CVD Event": cvd_event if 'cvd_event' in locals() else "No",
                # ... (Include all other variables here)
            }])
            
            # Update Google Sheet
            existing_data = conn.read(worksheet="Sheet1")
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("🎉 Data successfully submitted! Thank you for your contribution.")
            st.balloons()
