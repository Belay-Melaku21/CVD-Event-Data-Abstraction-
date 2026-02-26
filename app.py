import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

# --- 1. የቁልፍ ስህተት መከላከያ (PRIVATE KEY FIX) ---
def get_cleaned_secrets():
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    # ቁልፉ ውስጥ ያሉ የተሳሳቱ የለይቶ ማቆያ ምልክቶችን ያጸዳል
    if "private_key" in secrets_dict:
        secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
    return secrets_dict

# --- 2. ደህንነት (AUTHENTICATION) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Clinical Data Portal Access")
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

# --- 3. ኢሜል መላኪያ ---
def send_submission_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'], msg['To'] = sender, "melakubelay93@gmail.com"
        msg['Subject'] = f"New CVD Entry - Study ID: {details.get('1.1 Study ID')}"
        body = "\n".join([f"{k}: {v}" for k, v in details.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"Email error: {e}")

# --- 4. ዋናው ፎርም ---
if check_password():
    st.title("Time to CVD Event Research Portal")
    st.markdown("---")
    
    # የዳታቤዝ ግንኙነት ሙከራ
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

    with st.form("cvd_checklist_form", clear_on_submit=True):
        # SECTION 1 & 2
        st.header("Section 1 & 2: Administrative & Eligibility")
        c1, c2 = st.columns(2)
        with c1:
            s_id = st.text_input("1.1 Study ID")
            fac = st.selectbox("1.2 Facility", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("1.3 Patient MRN")
        with c2:
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed (Hypertensive)", "2= Unexposed (Normotensive)"])
            enrol_dt = st.text_input("1.5 Enrollment Date (DD/MM/YYYY E.C.)")
            fup_dt = st.text_input("1.6 Follow-up End Date (DD/MM/YYYY E.C.)")
        
        st.subheader("Eligibility Check")
        e1 = st.radio("2.1 Age ≥18 years?", ["1=Yes", "2=No"])
        e2 = st.radio("2.2 Pre-existing CVD?", ["1=Yes", "2=No"])
        e3 = st.radio("2.3 Pregnancy-induced HTN?", ["1=Yes", "2=No"])

        # SECTION 3: SOCIO-DEMOGRAPHIC
        st.header("Section 3: Socio-Demographic")
        age = st.number_input("3.3 Age", min_value=18)
        sex = st.radio("3.4 Sex", ["1=Male", "2=Female"])
        res = st.radio("3.5 Residence", ["1=Urban", "2=Rural"])
        edu = st.selectbox("3.6 Education", ["1=No formal", "2=Primary", "3=Secondary", "4=Higher"])
        occ = st.selectbox("3.7 Occupation", ["1=Gov Employee", "2=Merchant", "3=Farmer", "4=Unemployed", "5=Other"])
        mar = st.selectbox("3.8 Marital Status", ["1=Single", "2=Married", "3=Widowed", "4=Divorced"])

        # SECTION 4: LIFESTYLE (Branching Logic)
        st.header("Section 4: Lifestyle & Behavioral")
        tobacco = st.selectbox("4.1 Tobacco", ["1=Never", "2=Current", "3=Previous"])
        alcohol = st.selectbox("4.2 Alcohol", ["1=Non-user", "2=Current User"])
        alc_freq = "NA"
        if alcohol == "2=Current User":
            alc_freq = st.text_input("4.2 Average drinks/day")
        khat = st.selectbox("4.3 Khat", ["1=Never", "2=Current", "3=History"])
        phys = st.radio("4.4 Physical Activity", ["1=Active", "2=Inactive"])
        salt = st.radio("4.5 Salt Intake", ["1=High", "2=Normal/Low"])

        # SECTION 5: CLINICAL (BMI Calculation)
        st.header("Section 5: Clinical Measurements")
        sbp = st.number_input("5.1 SBP (mmHg)")
        dbp = st.number_input("5.1 DBP (mmHg)")
        htn_stg = st.selectbox("5.2 HTN Stage", ["1=Pre-HTN", "2=Stage 1", "3=Stage 2", "4=Stage 3/4"])
        
        w = st.number_input("5.3 Weight (kg)", min_value=1.0)
        h = st.number_input("5.3 Height (cm)", min_value=1.0)
        bmi = round(w / ((h/100)**2), 2)
        bmi_cat = "Normal"
        if bmi < 18.5: bmi_cat = "1=Underweight"
        elif 18.5 <= bmi < 25: bmi_cat = "2=Normal"
        elif 25 <= bmi < 30: bmi_cat = "3=Overweight"
        else: bmi_cat = "4=Obese"
        st.info(f"Calculated BMI: {bmi} ({bmi_cat})")

        htn_dur = st.text_input("5.5 HTN Duration (months)")
        fam_hx = st.radio("5.6 Family History of CVD", ["1=Yes", "2=No"])

        # SECTION 6: BIOCHEMICAL
        st.header("Section 6: Biochemical Profile")
        dm = st.radio("6.1 DM", ["1=Yes", "2=No"])
        ckd = st.radio("6.2 CKD", ["1=Yes", "2=No"])
        prot = st.radio("6.3 Proteinuria", ["1=Positive", "2=Negative"])
        chol = st.text_input("6.4 Total Cholesterol (mg/dL) - write NA if missing")
        base_comp = st.selectbox("6.5 Baseline Complications", ["1=None", "2=Prior Stroke", "3=Prior Cardiac"])

        # SECTION 7: TREATMENT
        st.header("Section 7: Treatment Factors")
        tx_type = st.selectbox("7.1 Med Type", ["1=Monotherapy", "2=Dual", "3=Poly"])
        tx_class = st.selectbox("7.2 Class", ["1=ACEi/ARB", "2=CCB", "3=Diuretics", "4=Beta-Blocker"])
        adh = st.radio("7.3 Adherence", ["1=Good", "2=Poor"])

        # SECTION 8: OUTCOME (Branching Logic)
        st.header("Section 8: Outcome & Survival")
        event = st.radio("8.1 CVD Event Occurred?", ["1=Yes", "2=No"])
        ev_type, ev_dt = "NA", "NA"
        if event == "1=Yes":
            ev_type = st.selectbox("8.2 Type", ["1=Stroke", "2=MI", "3=HF"])
            ev_dt = st.text_input("8.3 Date of Event")
        
        cens = st.selectbox("8.4 Censoring Details", ["1=Lost to Follow-up", "2=Died (Non-CVD)", "3=Study ended"])
        last_dt = st.text_input("8.5 Last Follow-up Date")

        if st.form_submit_button("Submit"):
            final_data = {
                "1.1 Study ID": s_id, "1.3 MRN": mrn, "1.2 Facility": fac, "1.4 Cohort": cohort,
                "BMI": bmi, "BMI Cat": bmi_cat, "Alcohol": alcohol, "Alc Freq": alc_freq,
                "8.1 CVD Event": event, "8.2 Event Type": ev_type, "8.3 Event Date": ev_dt,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            # ወደ Google Sheet መላክ
            df = pd.DataFrame([final_data])
            existing = conn.read()
            updated = pd.concat([existing, df], ignore_index=True)
            conn.update(data=updated)
            
            # ኢሜል መላክ
            send_submission_email(final_data)
            st.success("Successfully Submitted! Check your email for confirmation.")
            st.balloons()
