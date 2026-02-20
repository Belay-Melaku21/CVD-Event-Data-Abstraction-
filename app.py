import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# የገጽ መዋቅር እና ርዕስ
st.set_page_config(page_title="CVD Research Data Portal", layout="wide")

# --- 1. ደህንነት (Login Section) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔒 የጥናት መረጃ መሰብሰቢያ (Belay Melaku)")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Incorrect username or password.")
    st.stop()

# --- 2. ዋናው አፕሊኬሽን ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Cardiovascular Disease (CVD) Event Data Abstraction Checklist")
st.write("**Study Title:** Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients on Follow-Up at Health Centers in Mehal Amhara Saynt District.")

# --- መግቢያ እና መመሪያ (Introduction & Confidentiality) ---
st.info("""
**Data Integrity & Confidentiality Notice:** Dear Healthcare Professional, please ensure that all data entered is accurate, consistent, and derived directly from the patient's medical records. Maintaining the highest level of confidentiality is paramount to the ethical standards of this research.
""")

st.success("""
**Professional Appreciation:** Thank you for your invaluable contribution to this research. Your diligence in completing this form accurately is deeply appreciated.
""")

st.markdown("---")

with st.form(key="cvd_data_form"):
    # SECTION 1: IDENTIFICATION & TRACKING
    st.header("SECTION 1: IDENTIFICATION & TRACKING")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = st.text_input("1.2. Patient Medical Record Number (MRN)")
    with col2:
        d_ext = st.date_input("1.3. Date of Data Extraction", datetime.now())
        d_enr = st.date_input("1.4. Date of Enrollment (Baseline Visit)")
    cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

    st.divider()

    # SECTION 2: ELIGIBILITY CHECKLIST
    st.header("SECTION 2: ELIGIBILITY CHECKLIST")
    age_elig = st.radio("2.1. Age ≥18 years?", ["Yes", "No"])
    cvd_elig = st.radio("2.2. Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["Yes", "No"])
    preg_elig = st.radio("2.3. Pregnancy-induced Hypertension?", ["Yes", "No"])
    
    if age_elig == "No" or cvd_elig == "Yes" or preg_elig == "Yes":
        st.warning("⚠️ This patient is NOT eligible for the study.")

    st.divider()

    # SECTION 3: SOCIO-DEMOGRAPHIC CHARACTERISTICS
    st.header("SECTION 3: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
    col3, col4 = st.columns(2)
    with col3:
        age = st.number_input("3.1. Age (in years)", min_value=0, max_value=120)
        sex = st.selectbox("3.2. Sex", ["Male", "Female"])
        residence = st.selectbox("3.3. Residence", ["Urban", "Rural"])
    with col4:
        edu = st.selectbox("3.4. Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        occ = st.selectbox("3.5. Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = st.selectbox("3.6. Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

    st.divider()

    # SECTION 4: LIFESTYLE & BEHAVIORAL FACTORS
    st.header("SECTION 4: LIFESTYLE & BEHAVIORAL FACTORS")
    col5, col6 = st.columns(2)
    with col5:
        tobacco = st.selectbox("4.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        alcohol = st.selectbox("4.2. Alcohol Consumption", ["Non-user", "Current User"])
        alc_qty = 0.0
        if alcohol == "Current User":
            alc_qty = st.number_input("Average standard drinks/day", min_value=0.0)
    with col6:
        khat = st.selectbox("4.3. Khat Chewing", ["Never", "Current User", "History of regular use"])
        phys = st.radio("4.4. Physical Activity (≥30 min/day, 5 days/week)", ["Physically Active", "Inactive"])
        salt = st.radio("4.5. Salt Intake", ["High (Adds salt to food)", "Normal/Low"])

    st.divider()

    # SECTION 5: CLINICAL & PHYSIOLOGICAL MEASUREMENTS
    st.header("SECTION 5: CLINICAL & PHYSIOLOGICAL MEASUREMENTS")
    col7, col8 = st.columns(2)
    with col7:
        sbp = st.number_input("5.1. Baseline SBP (mmHg)", min_value=0)
        dbp = st.number_input("5.1. Baseline DBP (mmHg)", min_value=0)
        wt = st.number_input("5.3. Weight (kg)", min_value=0.0)
        ht = st.number_input("5.3. Height (cm)", min_value=0.0)
    
    with col8:
        # BMI Calculation logic
        bmi_val = 0.0
        bmi_cat = "N/A"
        if ht > 0:
            bmi_val = round(wt / ((ht/100)**2), 2)
            if bmi_val < 18.5: bmi_cat = "Underweight (<18.5)"
            elif 18.5 <= bmi_val < 25: bmi_cat = "Normal"
            elif 25 <= bmi_val < 30: bmi_cat = "Overweight (25-29.9)"
            else: bmi_cat = "Obese (≥30)"
        
        st.info(f"5.3. Calculated BMI: {bmi_val}")
        st.info(f"5.4. BMI Category: {bmi_cat}")
        htn_stg = st.selectbox("5.2. Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
        htn_dur = st.text_input("5.5. Duration of HTN (months/years)")
        fam_hx = st.radio("5.6. Family History of CVD/HTN", ["Yes", "No"])

    st.divider()

    # SECTION 6: BIOCHEMICAL & COMORBIDITY PROFILE
    st.header("SECTION 6: BIOCHEMICAL & COMORBIDITY PROFILE")
    col9, col10 = st.columns(2)
    with col9:
        dm = st.radio("6.1. Diabetes Mellitus (DM)", ["Yes", "No"])
        ckd = st.radio("6.2. Chronic Kidney Disease (CKD)", ["Yes", "No"])
        proteinuria = st.selectbox("6.3. Proteinuria", ["Positive", "Negative"])
    with col10:
        cholesterol = st.number_input("6.4. Total Cholesterol (mg/dL)", min_value=0.0)
        complications = st.multiselect("6.5. Baseline Complications", ["None", "Prior Stroke", "Prior Cardiac issues"])

    st.divider()

    # SECTION 7: TREATMENT & MANAGEMENT FACTORS
    st.header("SECTION 7: TREATMENT & MANAGEMENT FACTORS")
    med_type = st.selectbox("7.1. Type of Antihypertensive Meds", ["Monotherapy", "Dual Therapy", "Polytherapy"])
    med_class = st.multiselect("7.2. Specific Class", ["ACEi/ARB", "CCB", "Diuretics", "Beta-Blockers"])
    adherence = st.radio("7.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

    st.divider()

    # SECTION 8: OUTCOME & SURVIVAL DATA
    st.header("SECTION 8: OUTCOME & SURVIVAL DATA")
    cvd_event = st.radio("8.1. CVD Event Occurred?", ["Yes", "No"])
    
    event_type = "N/A"
    d_event = None
    if cvd_event == "Yes":
        col11, col12 = st.columns(2)
        with col11:
            event_type = st.selectbox("8.2. Type of CVD Event", ["Stroke (Ischemic/Hemorrhagic)", "Myocardial Infarction", "Heart Failure"])
        with col12:
            d_event = st.date_input("8.3. Date of CVD Event")

    censor = st.selectbox("8.4. Censoring Details", ["N/A", "Lost to Follow-up", "Died (Non-CVD cause)", "Study ended without event"])
    d_last = st.date_input("8.5. Date of Last Follow-up/Censoring")

    # Submit Button
    submit_button = st.form_submit_button(label="Submit Data")

    if submit_button:
        new_row = {
            "HC_Name": h_center, "MRN": mrn, "Date_Extraction": str(d_ext), "Date_Enrollment": str(d_enr),
            "Cohort": cohort, "Age": age, "Sex": sex, "Residence": residence, "Education": edu,
            "Occupation": occ, "Marital": marital, "Tobacco": tobacco, "Alcohol": alcohol,
            "Alc_Qty": alc_qty, "Khat": khat, "Physical_Activity": phys, "Salt": salt,
            "SBP": sbp, "DBP": dbp, "HTN_Stage": htn_stg, "BMI": bmi_val, "BMI_Category": bmi_cat,
            "HTN_Duration": htn_dur, "Family_Hx": fam_hx, "DM": dm, "CKD": ckd, "Proteinuria": proteinuria,
            "Cholesterol": cholesterol, "Complications": str(complications), "Med_Type": med_type,
            "Med_Class": str(med_class), "Adherence": adherence, "CVD_Event": cvd_event,
            "Event_Type": event_type, "Date_Event": str(d_event), "Censor_Details": censor, "Date_Last_Followup": str(d_last)
        }

        try:
            df = conn.read()
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ Data successfully recorded!")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
