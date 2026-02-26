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
        st.warning(f"Email error: {e}")

if check_password():
    st.title("Time to CVD Event Research Portal")
    
    # --- 3. የዳታቤዝ ግንኙነት (Fixed Connection) ---
    try:
        # ሚስጥራዊ ቁልፉን (Private Key) እና ግንኙነቱን ማስተካከል
        conn_params = st.secrets["connections"]["gsheets"].to_dict()
        if "private_key" in conn_params:
            conn_params["private_key"] = conn_params["private_key"].replace("\\n", "\n")
        
        # ስህተቱን ለማስወገድ 'type' የሚለውን ቁልፍ ከ params ውስጥ እናወጣዋለን
        if "type" in conn_params:
            del conn_params["type"]
            
        conn = st.connection("gsheets", type=GSheetsConnection, **conn_params)
    except Exception as e:
        st.error(f"Database Error: {e}")
        st.stop()

    with st.form("cvd_full_checklist", clear_on_submit=True):
        # Section 1 & 2: Administrative & Eligibility
        st.header("Section 1 & 2: Administrative & Eligibility")
        c1, c2 = st.columns(2)
        with c1:
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("1.3 Patient MRN")
        with c2:
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed", "2= Unexposed"])
            enrol_date = st.text_input("1.5 Date of Enrollment (DD/MM/YYYY E.C.)")
            fup_end = st.text_input("1.6 Follow-up End Date (DD/MM/YYYY E.C.)")
        
        st.subheader("Eligibility Checklist")
        age_elig = st.radio("2.1 Age ≥18 years?", ["1 = Yes", "2 = No"])
        pre_cvd = st.radio("2.2 Pre-existing CVD?", ["1 = Yes", "2 = No"])
        preg_htn = st.radio("2.3 Pregnancy-induced HTN?", ["1 = Yes", "2 = No"])

        # Section 3 & 4: Demographic & Lifestyle
        st.header("Section 3 & 4: Socio-Demographic & Lifestyle")
        age = st.number_input("3.3 Age (years)", min_value=18)
        sex = st.radio("3.4 Sex", ["1 = Male", "2 = Female"])
        edu = st.selectbox("3.6 Education", ["1=No formal", "2=Primary", "3=Secondary", "4=Higher"])
        tobacco = st.selectbox("4.1 Tobacco Use", ["1=Never", "2=Current", "3=Previous"])
        alcohol = st.selectbox("4.2 Alcohol", ["1 = Non-user", "2 = Current User"])
        
        # Section 5: Clinical (BMI Calculation)
        st.header("Section 5: Clinical Measurements")
        sbp = st.number_input("5.1 SBP (mmHg)")
        dbp = st.number_input("5.1 DBP (mmHg)")
        weight = st.number_input("5.3 Weight (kg)")
        height = st.number_input("5.3 Height (cm)")
        
        bmi = 0
        if weight > 0 and height > 0:
            bmi = round(weight / ((height/100)**2), 2)
            st.info(f"Calculated BMI: {bmi}")

        # Section 6 & 7: Biochemical & Treatment
        st.header("Section 6 & 7: Biochemical & Treatment")
        dm = st.radio("6.1 Diabetes?", ["1=Yes", "2=No"])
        ckd = st.radio("6.2 CKD?", ["1=Yes", "2=No"])
        tx_type = st.selectbox("7.1 Med Type", ["1=Monotherapy", "2=Dual", "3=Poly"])

        # Section 8: Outcome & Survival
        st.header("Section 8: Outcome & Survival Data")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["1 = Yes", "2 = No"])
        ev_date = st.text_input("8.3 Date of CVD Event") if cvd_event == "1 = Yes" else "NA"
        last_fup = st.text_input("8.5 Date of Last Follow-up")

        if st.form_submit_button("Submit Record"):
            # መረጃውን ማጠቃለል
            final_data = {
                "1.1 Study ID": study_id, "1.3 MRN": mrn, "1.2 Facility": facility,
                "BMI": bmi, "8.1 CVD Event": cvd_event, "8.3 Event Date": ev_date,
                "8.5 Last Date": last_fup, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # ወደ Google Sheet መላክ
                df = pd.DataFrame([final_data])
                conn.create(data=df)
                send_submission_email(final_data)
                st.success("Record Submitted Successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Submission Error: {e}")
