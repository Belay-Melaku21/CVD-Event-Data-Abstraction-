import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from ethiopian_date import EthiopianDateConverter
from datetime import datetime

st.set_page_config(page_title="CVD Research Portal", layout="wide")

# የኢትዮጵያ ቀን መቀየሪያ logic (ከስህተት የጸዳ)
def to_ethiopian(gregorian_date):
    if gregorian_date:
        try:
            eth = EthiopianDateConverter.to_ethiopian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
            return f"{eth[2]}/{eth[1]}/{eth[0]}"
        except Exception:
            return "N/A"
    return "N/A"

# --- 1. ደህንነት (Login) ---
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
            st.error("ስህተት ያስገቡ!")
    st.stop()

# --- 2. ዋናው አፕሊኬሽን ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Cardiovascular Disease (CVD) Event Data Abstraction Form")
st.write("**Study Title:** Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients on Follow-Up at Health Centers in Mehal Amhara Saynt District.")

# --- ፕሮፌሽናል መግቢያ እና ምስጋና ---
st.info("""
**Data Integrity & Confidentiality Notice:** Dear Healthcare Professional, please ensure that all data entered is accurate, consistent, and derived directly from the patient's medical records. Maintaining the highest level of confidentiality is paramount to the ethical standards of this research. Your commitment to data quality is the foundation of this study.
""")

st.success("""
**Professional Appreciation:** Thank you for your invaluable contribution to this research. Your time and professional diligence in completing this abstraction form accurately are deeply appreciated.
""")

st.markdown("---")

with st.form(key="cvd_final_form"):
    # SECTION 1: IDENTIFICATION & TRACKING
    st.header("SECTION 1: IDENTIFICATION & TRACKING")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.text_input("1.1. Health Center Name")
        mrn = st.text_input("1.2. Patient Medical Record Number (MRN)")
    with col2:
        d_ext_g = st.date_input("1.3. Date of Data Extraction (Gregorian)", value=datetime.now())
        d_enr_g = st.date_input("1.4. Date of Enrollment (Gregorian)")
        st.write(f"የኢትዮጵያ ቀን (Enrollment): **{to_ethiopian(d_enr_g)}**")
    
    cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

    st.divider()

    # SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS
    st.header("SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
    col3, col4 = st.columns(2)
    with col3:
        age = st.number_input("2.1. Age (in years)", min_value=0, max_value=120)
        sex = st.selectbox("2.2. Sex", ["Male", "Female"])
        res = st.selectbox("2.3. Residence", ["Urban", "Rural"])
    with col4:
        edu = st.selectbox("2.4. Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        occ = st.selectbox("2.5. Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = st.selectbox("2.6. Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

    st.divider()

    # SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS
    st.header("SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS")
    col5, col6 = st.columns(2)
    with col5:
        tobacco = st.selectbox("3.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        alcohol = st.selectbox("3.2. Alcohol Consumption", ["Non-user", "Current User"])
        alc_qty = 0.0
        if alcohol == "Current User":
            alc_qty = st.number_input("Avg. drinks/day", min_value=0.0)
    with col6:
        khat = st.selectbox("3.3. Khat Chewing", ["Never", "Current User", "History of regular use"])
        phys = st.radio("3.4. Physical Activity (≥30 min/day)", ["Physically Active", "Inactive"])
        salt = st.radio("3.5. Salt Intake", ["High (Adds salt to food)", "Normal/Low"])

    st.divider()

    # SECTION 4: CLINICAL MEASUREMENTS (Smart BMI)
    st.header("SECTION 4: CLINICAL MEASUREMENTS")
    col7, col8 = st.columns(2)
    with col7:
        sbp = st.number_input("4.1. Baseline SBP (mmHg)", min_value=0)
        dbp = st.number_input("4.1. Baseline DBP (mmHg)", min_value=0)
        wt = st.number_input("4.3. Weight (kg)", min_value=0.0)
        ht = st.number_input("4.3. Height (cm)", min_value=0.0)
    
    with col8:
        bmi_val = 0.0
        bmi_cat_auto = "N/A"
        if ht > 0:
            bmi_val = round(wt / ((ht/100)**2), 2)
            if bmi_val < 18.5: bmi_cat_auto = "Underweight (<18.5)"
            elif 18.5 <= bmi_val < 25: bmi_cat_auto = "Normal"
            elif 25 <= bmi_val < 30: bmi_cat_auto = "Overweight (25-29.9)"
            else: bmi_cat_auto = "Obese (≥30)"
        
        st.info(f"4.3. Calculated BMI: {bmi_val} kg/m²")
        st.info(f"4.4. Auto-Selected Category: {bmi_cat_auto}")
        htn_stg = st.selectbox("4.2. Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
        htn_dur = st.text_input("4.5. Duration of HTN")
        fam_hx = st.radio("4.6. Family History of CVD/HTN", ["Yes", "No"])

    st.divider()

    # SECTION 5 & 6: BIOCHEMICAL & TREATMENT
    st.header("SECTION 5 & 6: BIOCHEMICAL & TREATMENT")
    col9, col10 = st.columns(2)
    with col9:
        dm = st.radio("5.1. Diabetes Mellitus (DM)", ["Yes", "No"])
        ckd = st.radio("5.2. Chronic Kidney Disease (CKD)", ["Yes", "No"])
        protein = st.selectbox("5.3. Proteinuria", ["Positive", "Negative"])
        chol = st.number_input("5.4. Total Cholesterol (mg/dL)", min_value=0.0)
    with col10:
        comp = st.multiselect("5.5. Baseline Complications", ["None", "Prior Stroke", "Prior Cardiac issues"])
        tx_type = st.selectbox("6.1. Treatment Type", ["Monotherapy", "Dual Therapy", "Polytherapy"])
        tx_adh = st.radio("6.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

    st.divider()

    # SECTION 7: OUTCOME & SURVIVAL DATA
    st.header("SECTION 7: OUTCOME & SURVIVAL DATA")
    cvd_event = st.radio("7.1. CVD Event Occurred?", ["Yes", "No"])
    
    event_type = "N/A"
    d_event_eth = "N/A"
    
    if cvd_event == "Yes":
        col11, col12 = st.columns(2)
        with col11:
            event_type = st.selectbox("7.2. Type of CVD Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
        with col12:
            d_ev_g = st.date_input("7.3. Date of CVD Event")
            d_event_eth = to_ethiopian(d_ev_g)
            st.write(f"የኢትዮጵያ ቀን (Event): **{d_event_eth}**")

    censor = st.selectbox("7.4. Censoring Details", ["N/A", "Lost to Follow-up", "Died (Non-CVD cause)", "Study ended without event"])
    d_last_g = st.date_input("7.5. Date of Last Follow-up/Censoring")
    st.write(f"የኢትዮጵያ ቀን (Follow-up): **{to_ethiopian(d_last_g)}**")

    # Final Submit Button
    submit_button = st.form_submit_button(label="Submit Final Data")

    if submit_button:
        new_row = {
            "Health_Center_Name": h_center, "Patient_MRN": mrn, 
            "Eth_Date_Extraction": to_ethiopian(d_ext_g),
            "Eth_Date_Enrollment": to_ethiopian(d_enr_g),
            "Age_Years": age, "Sex": sex, "Calculated_BMI": bmi_val, 
            "BMI_Category": bmi_cat_auto, "CVD_Event_Occurred": cvd_event,
            "Type_of_CVD_Event": event_type, "Eth_Date_of_Event": d_event_eth,
            "Eth_Date_of_Last_Followup": to_ethiopian(d_last_g)
        }
        
        try:
            df = conn.read()
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ Data successfully recorded! Thank you for your professional contribution.")
            st.balloons()
        except Exception as e:
            st.error(f"Error saving to Sheet: {e}")
