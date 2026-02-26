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

# --- 2. የኢሜል ማሳወቂያ ---
def send_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'], msg['To'] = sender, "melakubelay93@gmail.com"
        msg['Subject'] = f"New CVD Entry - ID: {details.get('Study ID')}"
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
    st.title("CVD Event Data Abstraction Portal")
    st.info("Authorized Personnel Only - Please ensure data integrity.")

    # --- 3. የዳታቤዝ ግንኙነት (FIXED) ---
    # በሴክሬትስ ውስጥ ያሉትን ስህተት የሚፈጥሩ ቁልፎችን ለይቶ በማውጣት ግንኙነቱን መፍጠር
    try:
        # 1. መጀመሪያ በ secrets ውስጥ ያለውን spreadsheet URL ለብቻ እንይዛለን
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # 2. ግንኙነቱን ያለምንም ተጨማሪ parameters እንፈጥራለን (Streamlit ራሱ ከ secrets ያገኘዋል)
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Database Error: {e}")
        st.stop()

    with st.form("main_form", clear_on_submit=True):
        # Section 1 & 2: Administrative
        st.header("Section 1 & 2: Administrative & Eligibility")
        c1, c2 = st.columns(2)
        with c1:
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
            mrn = st.text_input("1.3 Patient MRN")
        with c2:
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed", "2= Unexposed"])
            enrol_dt = st.text_input("1.5 Enrollment Date (DD/MM/YYYY E.C.)")
            fup_end = st.text_input("1.6 Follow-up End Date (DD/MM/YYYY E.C.)")

        # Section 3: Socio-Demographic
        st.header("Section 3: Socio-Demographic")
        age = st.number_input("3.3 Age", min_value=18)
        sex = st.radio("3.4 Sex", ["1=Male", "2=Female"])
        residence = st.radio("3.5 Residence", ["1=Urban", "2=Rural"])
        edu = st.selectbox("3.6 Education", ["1=No formal", "2=Primary", "3=Secondary", "4=Higher"])
        occ = st.selectbox("3.7 Occupation", ["1=Gov Employee", "2=Merchant", "3=Farmer", "4=Unemployed", "5=Other"])

        # Section 4 & 5: Lifestyle & Clinical
        st.header("Section 4 & 5: Lifestyle & Clinical")
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["1=Non-user", "2=Current User"])
        alc_freq = st.text_input("Frequency (if current user)", "NA") if alcohol == "2=Current User" else "NA"
        
        weight = st.number_input("5.3 Weight (kg)", min_value=1.0)
        height = st.number_input("5.3 Height (cm)", min_value=1.0)
        
        bmi = round(weight / ((height/100)**2), 2) if weight > 0 else 0
        bmi_cat = "Normal"
        if bmi < 18.5: bmi_cat = "1=Underweight"
        elif 18.5 <= bmi < 25: bmi_cat = "2=Normal"
        elif 25 <= bmi < 30: bmi_cat = "3=Overweight"
        else: bmi_cat = "4=Obese"
        st.info(f"BMI: {bmi} ({bmi_cat})")

        # Section 8: Outcome
        st.header("Section 8: Outcome Data")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["1=Yes", "2=No"])
        event_type = st.selectbox("8.2 Type", ["Stroke", "MI", "HF"]) if cvd_event == "1=Yes" else "NA"
        last_visit = st.text_input("8.5 Last Follow-up/Censoring Date")

        if st.form_submit_button("Submit Record"):
            data_to_save = {
                "Study ID": study_id, "MRN": mrn, "Facility": facility,
                "BMI": bmi, "CVD Event": cvd_event, "Event Type": event_type,
                "Last Date": last_visit, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # ዳታውን ወደ Sheet መላክ
                df = pd.DataFrame([data_to_save])
                conn.create(spreadsheet=sheet_url, data=df)
                send_email(data_to_save)
                st.success("Record submitted successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Save Error: {e}")
