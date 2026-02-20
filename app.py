import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from ethiopian_date import EthiopianDateConverter
from datetime import datetime

st.set_page_config(page_title="CVD Research Portal - Ethiopian Calendar", layout="wide")

# የኢትዮጵያ ቀን መቀየሪያ Function
def to_ethiopian(gregorian_date):
    if gregorian_date:
        eth = EthiopianDateConverter.to_ethiopian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        return f"{eth[2]}/{eth[1]}/{eth[0]}" # DD/MM/YYYY format
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
st.title("📋 CVD Event Data Abstraction Form (Ethiopian Calendar)")

with st.form(key="cvd_ethiopian_form"):
    # SECTION 1: IDENTIFICATION [cite: 3]
    st.header("SECTION 1: IDENTIFICATION & TRACKING")
    col1, col2 = st.columns(2)
    with col1:
        h_center = st.text_input("1.1. Health Center Name") [cite: 4]
        mrn = st.text_input("1.2. Patient MRN") [cite: 5]
    with col2:
        # እዚህ ጋር ተጠቃሚው በፈረንጅ ቀን ይመርጣል፣ አፑ ወደ ኢትዮጵያ ቀን ይቀይረዋል
        d_ext_g = st.date_input("1.3. Date of Extraction (Select Gregorian)") [cite: 6]
        d_enr_g = st.date_input("1.4. Date of Enrollment (Select Gregorian)") [cite: 7]
        st.write(f"የኢትዮጵያ ቀን (Extraction): **{to_ethiopian(d_ext_g)}**")
        st.write(f"የኢትዮጵያ ቀን (Enrollment): **{to_ethiopian(d_enr_g)}**")
    cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"]) [cite: 8]

    st.divider()

    # SECTION 2: SOCIO-DEMOGRAPHIC [cite: 9]
    st.header("SECTION 2: SOCIO-DEMOGRAPHIC")
    col3, col4 = st.columns(2)
    with col3:
        age = st.number_input("2.1. Age (years)", min_value=0) [cite: 10]
        sex = st.selectbox("2.2. Sex", ["Male", "Female"]) [cite: 11]
        res = st.selectbox("2.3. Residence", ["Urban", "Rural"]) [cite: 12]
    with col4:
        edu = st.selectbox("2.4. Education", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"]) [cite: 13]
        occ = st.selectbox("2.5. Occupation", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"]) [cite: 14]
        marital = st.selectbox("2.6. Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"]) [cite: 15]

    st.divider()

    # SECTION 3: LIFESTYLE (Conditional Logic) [cite: 16]
    st.header("SECTION 3: LIFESTYLE")
    col5, col6 = st.columns(2)
    with col5:
        tobacco = st.selectbox("3.1. Tobacco Use", ["Never", "Current", "Previous"]) [cite: 17]
        alcohol = st.selectbox("3.2. Alcohol Consumption", ["Non-user", "Current User"]) [cite: 18]
        alc_qty = 0.0
        if alcohol == "Current User":
            alc_qty = st.number_input("Avg. drinks/day", min_value=0.0) [cite: 18]
    with col6:
        khat = st.selectbox("3.3. Khat Chewing", ["Never", "Current", "History"]) [cite: 19]
        phys = st.radio("3.4. Physical Activity", ["Physically Active", "Inactive"]) [cite: 20]
        salt = st.radio("3.5. Salt Intake", ["High", "Normal/Low"]) [cite: 21]

    st.divider()

    # SECTION 4: CLINICAL (Smart BMI) [cite: 22]
    st.header("SECTION 4: CLINICAL MEASUREMENTS")
    col7, col8 = st.columns(2)
    with col7:
        sbp = st.number_input("4.1. Baseline SBP (mmHg)", min_value=0) [cite: 23]
        dbp = st.number_input("4.1. Baseline DBP (mmHg)", min_value=0) [cite: 23]
        wt = st.number_input("4.3. Weight (kg)", min_value=0.0) [cite: 25]
        ht = st.number_input("4.3. Height (cm)", min_value=0.0) [cite: 25]
    
    with col8:
        # BMI Calculation logic [cite: 25]
        bmi_val = 0.0
        bmi_cat = "N/A"
        if ht > 0:
            bmi_val = round(wt / ((ht/100)**2), 2)
            if bmi_val < 18.5: bmi_cat = "Underweight (<18.5)"
            elif 18.5 <= bmi_val < 25: bmi_cat = "Normal"
            elif 25 <= bmi_val < 30: bmi_cat = "Overweight (25-29.9)"
            else: bmi_cat = "Obese (≥30)" [cite: 26]
        
        st.info(f"4.3. Calculated BMI: {bmi_val}") [cite: 25]
        st.info(f"4.4. Auto-Selected Category: {bmi_cat}") [cite: 26]
        htn_stg = st.selectbox("4.2. HTN Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"]) [cite: 24]
        htn_dur = st.text_input("4.5. Duration of HTN") [cite: 27]

    st.divider()

    # SECTION 5 & 6: BIOCHEMICAL & TREATMENT [cite: 29, 35]
    st.header("SECTION 5 & 6: BIOCHEMICAL & TREATMENT")
    col9, col10 = st.columns(2)
    with col9:
        dm = st.radio("5.1. DM", ["Yes", "No"]) [cite: 30]
        ckd = st.radio("5.2. CKD", ["Yes", "No"]) [cite: 31]
        protein = st.selectbox("5.3. Proteinuria", ["Positive", "Negative"]) [cite: 32]
    with col10:
        med_type = st.selectbox("6.1. Treatment Type", ["Monotherapy", "Dual", "Polytherapy"]) [cite: 36]
        adherence = st.radio("6.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"]) [cite: 38]

    st.divider()

    # SECTION 7: OUTCOME [cite: 39]
    st.header("SECTION 7: OUTCOME")
    cvd_event = st.radio("7.1. CVD Event Occurred?", ["Yes", "No"]) [cite: 40]
    
    event_type = "N/A"
    d_event_eth = "N/A"
    
    if cvd_event == "Yes":
        col11, col12 = st.columns(2)
        with col11:
            event_type = st.selectbox("7.2. Type of Event", ["Stroke", "Myocardial Infarction", "Heart Failure"]) [cite: 41]
        with col12:
            d_ev_g = st.date_input("7.3. Date of Event (Gregorian)") [cite: 42]
            d_event_eth = to_ethiopian(d_ev_g)
            st.write(f"የኢትዮጵያ ቀን (Event): **{d_event_eth}**")

    d_last_g = st.date_input("7.5. Date of Last Follow-up (Gregorian)") [cite: 44]
    st.write(f"የኢትዮጵያ ቀን (Follow-up): **{to_ethiopian(d_last_g)}**")

    submit = st.form_submit_button("Submit Data to Google Sheet")

    if submit:
        # መረጃውን ማደራጀት (የኢትዮጵያ ቀን ተካቷል)
        new_row = {
            "Health_Center_Name": h_center, "Patient_MRN": mrn, 
            "Eth_Date_Extraction": to_ethiopian(d_ext_g),
            "Eth_Date_Enrollment": to_ethiopian(d_enr_g),
            "Age_Years": age, "Sex": sex, "Alcohol_Consumption": alcohol, 
            "Avg_Drinks_Per_Day": alc_qty, "Calculated_BMI": bmi_val, 
            "BMI_Category": bmi_cat, "CVD_Event_Occurred": cvd_event,
            "Type_of_CVD_Event": event_type, "Eth_Date_of_Event": d_event_eth,
            "Eth_Date_of_Last_Followup": to_ethiopian(d_last_g)
        }
        
        try:
            df = conn.read()
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("ዳታው በኢትዮጵያ ቀን አቆጣጠር በስኬት ተቀምጧል!")
        except Exception as e:
            st.error(f"Error: {e}")
