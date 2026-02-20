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
[cite_start]st.write("**Study Title:** Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients on Follow-Up at Health Centers in Mehal Amhara Saynt District. [cite: 2]")

# --- ፕሮፌሽናል መግቢያ እና ምስጋና ---
st.info("""
**Data Integrity & Confidentiality Notice:** *Dear Healthcare Professional, please ensure that all data entered is accurate, consistent, and derived directly from the patient's medical records. Maintaining the highest level of confidentiality is paramount to the ethical standards of this research. Your commitment to data quality is the foundation of this study.*
""")

st.success("""
**Professional Appreciation:** *Thank you for your invaluable contribution to this research. Your time and professional diligence in completing this abstraction form accurately are deeply appreciated.*
""")

st.markdown("---")

with st.form(key="cvd_final_corrected_form"):
    # [cite_start]SECTION 1: IDENTIFICATION & TRACKING [cite: 3]
    st.header("SECTION 1: IDENTIFICATION & TRACKING")
    col1, col2 = st.columns(2)
    with col1:
        [cite_start]h_center = st.text_input("1.1. Health Center Name [cite: 4]")
        [cite_start]mrn = st.text_input("1.2. Patient Medical Record Number (MRN) [cite: 5]")
    with col2:
        [cite_start]d_ext_g = st.date_input("1.3. Date of Data Extraction (Gregorian) [cite: 6]", value=datetime.now())
        [cite_start]d_enr_g = st.date_input("1.4. Date of Enrollment (Gregorian) [cite: 7]")
        st.write(f"የኢትዮጵያ ቀን (Enrollment): **{to_ethiopian(d_enr_g)}**")
    
    [cite_start]cohort = st.radio("1.5. Cohort Status [cite: 8]", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

    st.divider()

    # [cite_start]SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS [cite: 9]
    st.header("SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
    col3, col4 = st.columns(2)
    with col3:
        [cite_start]age = st.number_input("2.1. Age (in years) [cite: 10]", min_value=0, max_value=120)
        [cite_start]sex = st.selectbox("2.2. Sex [cite: 11]", ["Male", "Female"])
        [cite_start]res = st.selectbox("2.3. Residence [cite: 12]", ["Urban", "Rural"])
    with col4:
        [cite_start]edu = st.selectbox("2.4. Educational Status [cite: 13]", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher (Diploma/Degree)"])
        [cite_start]occ = st.selectbox("2.5. Occupational Status [cite: 14]", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        [cite_start]marital = st.selectbox("2.6. Marital Status [cite: 15]", ["Single", "Married", "Widowed", "Divorced/Separated"])

    st.divider()

    # [cite_start]SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS [cite: 16]
    st.header("SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS")
    col5, col6 = st.columns(2)
    with col5:
        [cite_start]tobacco = st.selectbox("3.1. Tobacco Use [cite: 17]", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        [cite_start]alcohol = st.selectbox("3.2. Alcohol Consumption [cite: 18]", ["Non-user", "Current User"])
        # Skip logic: አልኮል ተጠቃሚ ከሆነ ብቻ
        alc_qty = 0.0
        if alcohol == "Current User":
            [cite_start]alc_qty = st.number_input("Avg. drinks/day [cite: 18]", min_value=0.0)
    with col6:
        [cite_start]khat = st.selectbox("3.3. Khat Chewing [cite: 19]", ["Never", "Current User", "History of regular use"])
        [cite_start]phys = st.radio("3.4. Physical Activity (≥30 min/day) [cite: 20]", ["Physically Active", "Inactive"])
        [cite_start]salt = st.radio("3.5. Salt Intake [cite: 21]", ["High (Adds salt to food)", "Normal/Low"])

    st.divider()

    # [cite_start]SECTION 4: CLINICAL MEASUREMENTS (Smart BMI) [cite: 22]
    st.header("SECTION 4: CLINICAL MEASUREMENTS")
    col7, col8 = st.columns(2)
    with col7:
        [cite_start]sbp = st.number_input("4.1. Baseline SBP (mmHg) [cite: 23]", min_value=0)
        [cite_start]dbp = st.number_input("4.1. Baseline DBP (mmHg) [cite: 23]", min_value=0)
        [cite_start]wt = st.number_input("4.3. Weight (kg) [cite: 25]", min_value=0.0)
        [cite_start]ht = st.number_input("4.3. Height (cm) [cite: 25]", min_value=0.0)
    
    with col8:
        # [cite_start]BMI Calculation logic [cite: 25]
        bmi_val = 0.0
        bmi_cat_auto = "N/A"
        if ht > 0:
            bmi_val = round(wt / ((ht/100)**2), 2)
            if bmi_val < 18.5: bmi_cat_auto = "Underweight (<18.5)"
            elif 18.5 <= bmi_val < 25: bmi_cat_auto = "Normal"
            elif 25 <= bmi_val < 30: bmi_cat_auto = "Overweight (25-29.9)"
            [cite_start]else: bmi_cat_auto = "Obese (≥30)" [cite: 26]
        
        st.info(f"4.3. Calculated BMI: {bmi_val} kg/m²")
        st.info(f"4.4. Auto-Selected Category: {bmi_cat_auto}")
        [cite_start]htn_stg = st.selectbox("4.2. Hypertension Stage [cite: 24]", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
        [cite_start]htn_dur = st.text_input("4.5. Duration of HTN [cite: 27]")
        [cite_start]fam_hx = st.radio("4.6. Family History of CVD/HTN [cite: 28]", ["Yes", "No"])

    st.divider()

    # [cite_start]SECTION 7: OUTCOME & SURVIVAL DATA [cite: 39]
    st.header("SECTION 7: OUTCOME & SURVIVAL DATA")
    [cite_start]cvd_event = st.radio("7.1. CVD Event Occurred? [cite: 40]", ["Yes", "No"])
    
    event_type = "N/A"
    d_event_eth = "N/A"
    
    # Skip logic: Event ካለ ብቻ
    if cvd_event == "Yes":
        col11, col12 = st.columns(2)
        with col11:
            [cite_start]event_type = st.selectbox("7.2. Type of CVD Event [cite: 41]", ["Stroke (Ischemic/Hemorrhagic)", "Myocardial Infarction", "Heart Failure"])
        with col12:
            [cite_start]d_ev_g = st.date_input("7.3. Date of CVD Event (Gregorian) [cite: 42]")
            d_event_eth = to_ethiopian(d_ev_g)
            st.write(f"የኢትዮጵያ ቀን (Event): **{d_event_eth}**")

    [cite_start]censor = st.selectbox("7.4. Censoring Details [cite: 43]", ["N/A", "Lost to Follow-up", "Died (Non-CVD cause)", "Study ended without event"])
    [cite_start]d_last_g = st.date_input("7.5. Date of Last Follow-up/Censoring (Gregorian) [cite: 44]")
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
