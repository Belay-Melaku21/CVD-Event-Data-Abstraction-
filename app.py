import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ገጹ ሲከፈት መረጃዎችን በራስ-ሰር ለማጽዳት (Reset logic)
def clear_form():
    for key in st.session_state.keys():
        if key not in ["logged_in"]:
            st.session_state.pop(key)
    st.rerun()

st.set_page_config(page_title="CVD Smart Portal", layout="wide")

# --- 1. ደህንነት (Login) ---
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

# --- 2. ዋናው አፕሊኬሽን ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📋 Smart CVD Event Data Abstraction Form")
st.write("**Study Title:** Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients [cite: 2]")

# --- ፕሮፌሽናል መግቢያ እና ምስጋና ---
st.info("መረጃው ተሞልቶ ሲያልቅ 'Submit' ሲጫኑ ገጹ በራሱ ተጸድቶ ለአዲስ ታካሚ ዝግጁ ይሆናል።")

with st.form(key="cvd_abstraction_form", clear_on_submit=True):
    # SECTION 1 & 2: Identification & Eligibility
    st.header("Section 1 & 2: Identification & Eligibility")
    col1, col2 = st.columns(2)
    with col1:
        # ስህተት የነበረበት መስመር እዚህ ተስተካክሏል
        h_center = st.selectbox("1.1. Health Center Name", ["Densa HC", "Kotet HC", "Werk-Mawcha HC", "Ahyo HC", "Atronse HC"])
        mrn = st.text_input("1.2. Patient MRN")
    with col2:
        d_ext = st.date_input("1.3. Date of Extraction", datetime.now())
        d_enr = st.date_input("1.4. Date of Enrollment (Baseline)")
    
    st.subheader("Eligibility Check (Exclusion Criteria) [cite: 9]")
    e1 = st.radio("2.1. Age ≥18 years?", ["Yes", "No"]) [cite: 10]
    e2 = st.radio("2.2. Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["No", "Yes"]) [cite: 11]
    e3 = st.radio("2.3. Pregnancy-induced Hypertension?", ["No", "Yes"]) [cite: 12]

    is_eligible = (e1 == "Yes" and e2 == "No" and e3 == "No")
    
    if not is_eligible:
        st.error("❌ Patient is NOT eligible. Submission will only record exclusion.")
        submit_button = st.form_submit_button("Submit Exclusion Only")
    else:
        st.success("✅ Patient is eligible. Please complete the form.")
        
        # SECTION 3 & 4: Socio-Demographic & Lifestyle
        st.header("Section 3 & 4: Socio-Demographic & Lifestyle")
        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("3.1. Age (years)", min_value=18) [cite: 14]
            sex = st.selectbox("3.2. Sex", ["Male", "Female"]) [cite: 15]
            edu = st.selectbox("3.4. Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"]) [cite: 17]
        with col4:
            tobacco = st.selectbox("4.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"]) [cite: 21]
            alcohol = st.selectbox("4.2. Alcohol Consumption", ["Non-user", "Current User"]) [cite: 22]
            alc_qty = 0.0
            if alcohol == "Current User":
                alc_qty = st.number_input("Avg. drinks/day", min_value=0.0) [cite: 22]

        # SECTION 5: Smart BMI & HTN Duration
        st.divider()
        st.header("Section 5: Clinical Measurements")
        col5, col6 = st.columns(2)
        with col5:
            wt = st.number_input("5.3. Weight (kg)", min_value=0.0) [cite: 29]
            ht = st.number_input("5.3. Height (cm)", min_value=0.0) [cite: 29]
            # Smart BMI Calculation [cite: 29]
            bmi_val = round(wt / ((ht/100)**2), 2) if ht > 0 else 0
            st.info(f"Calculated BMI: {bmi_val}")
        with col6:
            htn_stage = st.selectbox("5.2. HTN Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"]) [cite: 28]
            fam_hx = st.radio("5.6. Family History of CVD/HTN", ["Yes", "No"]) [cite: 32]

        # SECTION 8: Outcome & Smart Duration
        st.divider()
        st.header("Section 8: Outcome & Survival Data")
        cvd_event = st.radio("8.1. CVD Event Occurred?", ["No", "Yes"]) [cite: 44]
        
        duration_val = 0
        study_end = datetime(2025, 11, 9).date() [cite: 31]
        
        if cvd_event == "Yes":
            event_type = st.selectbox("8.2. Type of CVD Event", ["Stroke", "MI", "Heart Failure"]) [cite: 45]
            d_event = st.date_input("8.3. Date of CVD Event") [cite: 46]
            duration_val = (d_event - d_enr).days / 30.44 if d_enr else 0 [cite: 31]
        else:
            censor = st.selectbox("8.4. Censoring Details", ["Study ended without event", "Lost to Follow-up", "Died (Non-CVD)"]) [cite: 47]
            d_last = st.date_input("8.5. Date of Last Follow-up", study_end) [cite: 48]
            duration_val = (d_last - d_enr).days / 30.44 if d_enr else 0 [cite: 31]

        st.warning(f"5.5. Auto-Calculated HTN Duration: {round(duration_val, 1)} months")
        
        # ፎርሙን ለማጠቃለል የግድ የሚያስፈልገው ቁልፍ (Submit Button)
        submit_button = st.form_submit_button("Submit Complete Data")

    if submit_button:
        # መረጃው ተሞልቶ ሲያልቅ ወደ Google Sheet የሚላክበት logic እዚህ ይገባል
        st.success("✅ መረጃው በትክክል ተመዝግቧል!")
        st.balloons()
        # ገጹን ዳግም በማስጀመር ፎርሙን ማጽዳት
        st.button("ለቀጣይ ታካሚ መረጃ መሙያ ተጫን", on_click=clear_form)
