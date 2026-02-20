import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ሺቱ መገናኘቱን ለማረጋገጥ መጀመሪያ መረጃውን እናንብብ
conn = st.connection("gsheets", type=GSheetsConnection)

# LOGIN logic (ቀደም ብለን የሰራነው)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Belay Melaku" and pwd == "@Belay6669":
            st.session_state["logged_in"] = True
            st.rerun()
else:
    st.success("እንኳን ደህና መጣህ በላይ!")
    
    # መረጃ መቀበያ ቅጽ (Form)
    with st.form("cvd_form"):
        # እዚህ ጋር ሁሉንም 39 የዳታ አይነቶች የሚቀበሉ Inputs ይገባሉ (ከላይ በሰጠሁህ ኮድ መሰረት)
        mrn = st.text_input("Patient MRN")
        h_center = st.text_input("Health Center Name")
        # ... ሌሎች ጥያቄዎች እዚህ ይቀጥላሉ ...
        
        submitted = st.form_submit_button("መረጃውን መዝግብ")
        
        if submitted:
            # አዲስ ዳታ መፍጠር
            new_row = pd.DataFrame([{"Health_Center_Name": h_center, "Patient_MRN": mrn}])
            
            # መረጃውን ወደ ሺቱ መላክ
            try:
                # ሺቱን አንብብ
                data = conn.read(worksheet="Sheet1")
                # አዲሱን ዳታ ጨምር
                updated_df = pd.concat([data, new_row], ignore_index=True)
                # ሺቱን አዘምን
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("መረጃው በስኬት ተመዝግቧል!")
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል: {e}")
