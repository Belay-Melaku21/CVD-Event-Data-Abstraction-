import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# የገጽ መዋቅር እና ርዕስ
st.set_page_config(page_title="CVD Research Data Portal", layout="wide")

# --- 1. ደህንነት (Login Section) ---
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.title("🔒 የጥናት መረጃ መሰብሰቢያ (Belay Melaku)")
        user = st.text_input("የተጠቃሚ ስም (Username)")
        pwd = st.text_input("ይለፍ ቃል (Password)", type="password")
        if st.button("ግባ (Login)"):
            if user == "Belay Melaku" and pwd == "@Belay6669":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ስህተት፡ እባክዎ ትክክለኛ መረጃ ያስገቡ!")
        return False
    return True

if check_password():
    # --- 2. ከGoogle Sheet ጋር ግንኙነት መፍጠር ---
    conn = st.connection("gsheets", type=GSheetsConnection)

    st.title("📋 Cardiovascular Disease (CVD) Event Data Abstraction Checklist")
    st.markdown("Study Title: **Time to Cardiovascular Disease Event and Its Determinant Among Hypertensive Patients on Follow-Up at Health Centers in Mehal Amhara Saynt District.**")

    with st.form(key="full_cvd_form"):
        # SECTION 1: IDENTIFICATION & TRACKING
        st.header("SECTION 1: IDENTIFICATION & TRACKING")
        col1, col2 = st.columns(2)
        with col1:
            h_center = st.text_input("1.1. Health Center Name")
            mrn = st.text_input("1.2. Patient Medical Record Number (MRN)")
        with col2:
            d_ext = st.date_input("1.3. Date of Data Extraction", datetime.now())
            d_enr = st.date_input("1.4. Date of Enrollment (Baseline Visit)")
        cohort = st.radio("1.5. Cohort Status", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])

        st.divider()

        # SECTION 2: SOCIO-DEMOGRAPHIC CHARACTERISTICS
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

        # SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS
        st.header("SECTION 3: LIFESTYLE & BEHAVIORAL FACTORS")
        col5, col6 = st.columns(2)
        with col5:
            tobacco = st.selectbox("3.1. Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
            alcohol = st.selectbox("3.2. Alcohol Consumption", ["Non-user", "Current User"])
            alc_qty = st.number_input("Avg. drinks/day (if current user)", min_value=0.0)
        with col6:
            khat = st.selectbox("3.3. Khat Chewing", ["Never", "Current User", "History of regular use"])
            phys = st.radio("3.4. Physical Activity (≥30 min/day)", ["Physically Active", "Inactive"])
            salt = st.radio("3.5. Salt Intake", ["High (Adds salt to food)", "Normal/Low"])

        st.divider()

        # SECTION 4: CLINICAL & PHYSIOLOGICAL MEASUREMENTS
        st.header("SECTION 4: CLINICAL & PHYSIOLOGICAL MEASUREMENTS")
        col7, col8 = st.columns(2)
        with col7:
            sbp = st.number_input("4.1. Baseline SBP (mmHg)", min_value=0)
            dbp = st.number_input("4.1. Baseline DBP (mmHg)", min_value=0)
            htn_stg = st.selectbox("4.2. Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
        with col8:
            wt = st.number_input("4.3. Weight (kg)", min_value=0.0)
            ht = st.number_input("4.3. Height (cm)", min_value=0.0)
            # BMI Calculation logic
            bmi_calc = round(wt / ((ht/100)**2), 2) if ht > 0 else 0
            st.write(f"**Calculated BMI: {bmi_calc}**")
            bmi_cat = st.selectbox("4.4. BMI Category", ["Underweight (<18.5)", "Normal", "Overweight (25-29.9)", "Obese (≥30)"])
        
        htn_dur = st.text_input("4.5. Duration of HTN (months/years)")
        fam_hx = st.radio("4.6. Family History of CVD/HTN", ["Yes", "No"])

        st.divider()

        # SECTION 5 & 6: BIOCHEMICAL & TREATMENT PROFILE
        st.header("SECTION 5 & 6: BIOCHEMICAL & TREATMENT PROFILE")
        col9, col10 = st.columns(2)
        with col9:
            dm = st.radio("5.1. Diabetes Mellitus (DM)", ["Yes", "No"])
            ckd = st.radio("5.2. Chronic Kidney Disease (CKD)", ["Yes", "No"])
            proteinuria = st.selectbox("5.3. Proteinuria", ["Positive", "Negative"])
            cholesterol = st.number_input("5.4. Total Cholesterol Level (mg/dL)", min_value=0.0)
        with col10:
            complications = st.multiselect("5.5. Baseline Complications", ["None", "Prior Stroke", "Prior Cardiac issues"])
            med_type = st.selectbox("6.1. Type of Antihypertensive Meds", ["Monotherapy", "Dual Therapy", "Polytherapy"])
            med_class = st.multiselect("6.2. Specific Class", ["ACEi/ARB", "CCB", "Diuretics", "Beta-Blockers"])
            adherence = st.radio("6.3. Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

        st.divider()

        # SECTION 7: OUTCOME & SURVIVAL DATA
        st.header("SECTION 7: OUTCOME & SURVIVAL DATA")
        cvd_event = st.radio("7.1. CVD Event Occurred?", ["Yes", "No"])
        event_type = st.selectbox("7.2. Type of CVD Event", ["N/A", "Stroke (Ischemic/Hemorrhagic)", "Myocardial Infarction", "Heart Failure"])
        d_event = st.date_input("7.3. Date of CVD Event", value=None)
        censor = st.selectbox("7.4. Censoring Details", ["N/A", "Lost to Follow-up", "Died (Non-CVD cause)", "Study ended without event"])
        d_last = st.date_input("7.5. Date of Last Follow-up/Censoring")

        # Submit Button
        submit_button = st.form_submit_button(label="መረጃውን ወደ Google Sheet ላክ (Submit Data)")

        if submit_button:
            # ሁሉንም መረጃ በኤክሴል ርዕሶች መሰረት ማደራጀት
            new_row = {
                "Health_Center_Name": h_center, "Patient_MRN": mrn, "Date_of_Extraction": str(d_ext),
                "Date_of_Enrollment": str(d_enr), "Cohort_Status": cohort, "Age_Years": age,
                "Sex": sex, "Residence": residence, "Educational_Status": edu,
                "Occupational_Status": occ, "Marital_Status": marital, "Tobacco_Use": tobacco,
                "Alcohol_Consumption": alcohol, "Avg_Drinks_Per_Day": alc_qty, "Khat_Chewing": khat,
                "Physical_Activity": phys, "Salt_Intake": salt, "Baseline_SBP": sbp,
                "Baseline_DBP": dbp, "Hypertension_Stage": htn_stg, "Weight_kg": wt,
                "Height_cm": ht, "Calculated_BMI": bmi_calc, "BMI_Category": bmi_cat,
                "Duration_of_HTN": htn_dur, "Family_History_CVD_HTN": fam_hx,
                "Diabetes_Mellitus": dm, "Chronic_Kidney_Disease": ckd, "Proteinuria": proteinuria,
                "Total_Cholesterol": cholesterol, "Baseline_Complications": str(complications),
                "Type_of_HTN_Meds": med_type, "Specific_Med_Class": str(med_class),
                "Medication_Adherence": adherence, "CVD_Event_Occurred": cvd_event,
                "Type_of_CVD_Event": event_type, "Date_of_CVD_Event": str(d_event),
                "Censoring_Details": censor, "Date_of_Last_Followup": str(d_last)
            }

            try:
                # ሺቱን ማንበብና አዲስ ዳታ መጨመር
                df = conn.read()
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=updated_df)
                st.success("✅ ሁሉም መረጃዎች በስኬት ተመዝግበዋል!")
                st.balloons()
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል፡ {e}")
