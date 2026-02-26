import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. ደህንነት (Authentication) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 CVD Research Portal Access")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pw == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        return False
    return True

# --- 2. ኢሜል ማሳወቂያ ---
def send_submission_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'], msg['To'] = sender, "melakubelay93@gmail.com"
        msg['Subject'] = f"New Study Record - ID: {details.get('1.1 Study ID')}"
        body = "\n".join([f"{k}: {v}" for k, v in details.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"Email notification error: {e}")

if check_password():
    st.title("Time to CVD Event & Determinants Study")
    st.info("Authorized Personnel Only - Data Abstraction Form")
    
    # --- 3. የዳታቤዝ ግንኙነት (Fixed Connection) ---
    try:
        # ሚስጥራዊ ቁልፉን ማስተካከል
        conn_params = st.secrets["connections"]["gsheets"].to_dict()
        
        # ስህተት የሚፈጥሩ ቁልፎችን (keys) ማስወገድ
        spreadsheet_url = conn_params.pop("spreadsheet", None)
        conn_params.pop("type", None) # 'type' ስህተት እንዳይፈጥር
        
        if "private_key" in conn_params:
            conn_params["private_key"] = conn_params["private_key"].replace("\\n", "\n")
        
        # ግንኙነቱን መፍጠር
        conn = st.connection("gsheets", type=GSheetsConnection, **conn_params)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

    with st.form("cvd_abstraction_form", clear_on_submit=True):
        # Section 1 & 2: Administrative & Eligibility
        st.header("Section 1 & 2: Administrative & Eligibility")
        c1, c2 = st.columns(2)
        with c1:
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("1.3 Patient MRN")
        with c2:
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed", "2= Unexposed"])
            enrol_date = st.text_input("1.5 Enrollment Date (DD/MM/YYYY E.C.)")
            fup_end = st.text_input("1.6 Follow-up End Date (DD/MM/YYYY E.C.)")
        
        st.subheader("Eligibility Checklist")
        age_elig = st.radio("2.1 Age ≥18 years?", ["1 = Yes", "2 = No"])
        pre_cvd = st.radio("2.2 Pre-existing CVD?", ["1 = Yes", "2 = No"])
        preg_htn = st.radio("2.3 Pregnancy-induced HTN?", ["1 = Yes", "2 = No"])

        # Section 3 & 4: Demographic & Lifestyle
        st.header("Section 3 & 4: Socio-Demographic & Lifestyle")
        age = st.number_input("3.3 Age (years)", min_value=18, step=1)
        sex = st.radio("3.4 Sex", ["1 = Male", "2 = Female"])
        residence = st.radio("3.5 Residence", ["1 = Urban", "2 = Rural"])
        edu = st.selectbox("3.6 Education", ["1=No formal", "2=Primary", "3=Secondary", "4=Higher"])
        occ = st.selectbox("3.7 Occupation", ["1=Gov Employee", "2=Merchant", "3=Farmer", "4=Unemployed", "5=Other"])
        marital = st.selectbox("3.8 Marital Status", ["1=Single", "2=Married", "3=Widowed", "4=Divorced"])
        
        tobacco = st.selectbox("4.1 Tobacco Use", ["1=Never", "2=Current", "3=Previous"])
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["1 = Non-user", "2 = Current User"])
        alc_freq = st.text_input("4.2 Drinks/day (if current user)", value="0")
        khat = st.selectbox("4.3 Khat Chewing", ["1=Never", "2=Current", "3=History"])
        phys_act = st.radio("4.4 Physical Activity", ["1=Active", "2=Inactive"])
        salt = st.radio("4.5 Salt Intake", ["1=High", "2=Normal/Low"])

        # Section 5: Clinical & BMI
        st.header("Section 5: Clinical Measurements")
        col_cl1, col_cl2 = st.columns(2)
        with col_cl1:
            sbp = st.number_input("5.1 SBP (mmHg)", min_value=0)
            dbp = st.number_input("5.1 DBP (mmHg)", min_value=0)
            htn_stage = st.selectbox("5.2 HTN Stage", ["1=Pre-HTN", "2=Stage 1", "3=Stage 2", "4=Stage 3/4"])
        with col_cl2:
            weight = st.number_input("5.3 Weight (kg)", min_value=0.0)
            height = st.number_input("5.3 Height (cm)", min_value=1.0)
            
            bmi = 0.0
            bmi_cat = "NA"
            if weight > 0 and height > 0:
                bmi = round(weight / ((height/100)**2), 2)
                if bmi < 18.5: bmi_cat = "1 = Underweight"
                elif 18.5 <= bmi < 25: bmi_cat = "2 = Normal"
                elif 25 <= bmi < 30: bmi_cat = "3 = Overweight"
                else: bmi_cat = "4 = Obese"
            st.info(f"Calculated BMI: {bmi} ({bmi_cat})")

        htn_dur = st.text_input("5.5 HTN Duration (months)")
        fam_hx = st.radio("5.6 Family History of CVD", ["1 = Yes", "2 = No"])

        # Section 6 & 7: Biochemical & Treatment
        st.header("Section 6 & 7: Biochemical & Treatment")
        dm = st.radio("6.1 Diabetes Mellitus", ["1 = Yes", "2 = No"])
        ckd = st.radio("6.2 CKD", ["1 = Yes", "2 = No"])
        proteinuria = st.radio("6.3 Proteinuria", ["1 = Positive", "2 = Negative"])
        cholesterol = st.text_input("6.4 Total Cholesterol (mg/dL)")
        baseline_comp = st.selectbox("6.5 Baseline Complications", ["1=None", "2=Prior Stroke", "3=Prior Cardiac"])
        
        tx_type = st.selectbox("7.1 Medication Type", ["1=Monotherapy", "2=Dual", "3=Poly"])
        tx_class = st.selectbox("7.2 Drug Class", ["1=ACEi/ARB", "2=CCB", "3=Diuretics", "4=Beta-Blocker"])
        adherence = st.radio("7.3 Adherence", ["1=Good", "2=Poor"])

        # Section 8: Outcome & Survival
        st.header("Section 8: Outcome Data")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["1 = Yes", "2 = No"])
        event_type = st.selectbox("8.2 Type", ["NA", "1=Stroke", "2=MI", "3=HF"]) if cvd_event == "1 = Yes" else "NA"
        event_date = st.text_input("8.3 Event Date") if cvd_event == "1 = Yes" else "NA"
        
        censoring = st.selectbox("8.4 Censoring", ["1=Lost to Follow-up", "2=Died (Non-CVD)", "3=Study ended"])
        last_visit = st.text_input("8.5 Last Follow-up/Censoring Date")

        # Submission
        if st.form_submit_button("Submit Data"):
            new_record = {
                "Study ID": study_id, "MRN": mrn, "Facility": facility, "Cohort": cohort,
                "Enrollment Date": enrol_date, "Age": age, "Sex": sex, "BMI": bmi, "BMI Cat": bmi_cat,
                "SBP": sbp, "DBP": dbp, "CVD Event": cvd_event, "Event Type": event_type, 
                "Event Date": event_date, "Last Visit": last_visit,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # ዳታውን ወደ Google Sheet መላክ (spreadsheet url እዚህ ጋር ጥቅም ላይ ይውላል)
                df = pd.DataFrame([new_record])
                conn.create(spreadsheet=spreadsheet_url, data=df)
                
                send_submission_email(new_record)
                st.success("Record Saved Successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving to Sheet: {e}")
