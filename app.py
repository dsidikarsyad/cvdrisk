import streamlit as st
import pickle
import pandas as pd
import Orange
from Orange.data.pandas_compat import table_from_frame
from streamlit_echarts import st_echarts

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Cardiovascular Risk Calculator",
    page_icon="🩺",
    layout="wide"
)  
# ---------------------------------------------------
# STYLE (COMPACT UI)
# ---------------------------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.3rem;
}
.stSelectbox label, .stTextInput label {
    font-size: 13px !important;
}
.stButton button {
    width: 100%;
    height: 2.8em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### 🩺 Cardiovascular Risk Calculator")
st.caption("⚠️ Disclaimer: This tool is intended for screening purposes only and does not replace professional medical judgment.") 
st.caption("Developed by D.S.Arsyad, S.A. Thamrin, et. al.") 
# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

@st.cache_resource
def load_model():
    with open("Random_Forest_new.pkcls", "rb") as f:
        model = pickle.load(f)
    return model

model = load_model()

# ---------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------

left, right = st.columns([2.2, 1])

# ---------------------------------------------------
# INPUT PANEL
# ---------------------------------------------------

with left:

    col1, col2, col3, col4 = st.columns(4)

    # COLUMN 1
    with col1:
        urban_rural = st.selectbox("Residence", ["Rural", "Urban"], index=None)
        sex = st.selectbox("Sex", ["Male", "Female"], index=None)
        marital = st.selectbox("Marital", ["Not Married", "Divorced", "Widowed", "Married"], index=None)
        education = st.selectbox("Education", [
            "College","University","Basic School","Senior High School",
            "Junior High School","Not Completed Basic School","Never Schooled"
        ], index=None)
        work = st.selectbox("Occupation", [
            "Daily workers","Others","Fisherman","Government Employee",
            "Private employee","Farmers","School/Student","Not Working","Entrepreneur"
        ], index=None)
        smoking = st.selectbox("Smoking Behavior", ["Never Smoke", "Quit Smoking", "Active Smokers"], index=None)
        alcohol = st.selectbox("Alcohol Consumption", ["No", "Yes"], index=None)

    # COLUMN 2
    with col2:
        history_diabetes = st.selectbox("History of Diabetes", ["No", "Yes"], index=None)
        history_ht = st.selectbox("History of Hypertension", ["No", "Yes"], index=None)
        history_renal = st.selectbox("History of Renal Disease", ["No", "Yes"], index=None)
        mental = st.selectbox("Mental Emotional Disorders", ["No", "Yes"], index=None)
        risky_food = st.selectbox("High Risk Diet", ["No", "Yes"], index=None)
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"], index=None)

    # COLUMN 3
    with col3:
        bmi = st.text_input("Body Mass Index (BMI)", placeholder="e.g. 22.5")
        waist = st.text_input("Waist circumference(cm)", placeholder="e.g. 80")
        sbp = st.text_input("Systolic BP (mmHg)", placeholder="e.g. 120")
        dbp = st.text_input("Diastolic BP (mmHg)", placeholder="e.g. 80")
        creat = st.text_input("Creatinine (mg/dL)", placeholder="e.g. 1.0")

    # COLUMN 4 (TEXT INPUT FOR EMPTY STATE)
    with col4:
        chol = st.text_input("Total Cholesterol (mg/dL)", placeholder="e.g. 180")
        hdl = st.text_input("HDL (mg/dL)", placeholder="e.g. 50")
        ldl = st.text_input("LDL(mg/dL)", placeholder="e.g. 100")
        trig = st.text_input("Triglyceride (mg/dL)", placeholder="e.g. 150")
       

    # ---------------------------------------------------
    # INPUT VALIDATION FUNCTIONS
    # ---------------------------------------------------

    def to_float(val, name):
        if val == "":
            return None
        try:
            return float(val)
        except:
            st.error(f"Invalid input for {name}")
            st.stop()

    # Convert inputs
    bmi = to_float(bmi, "BMI")
    waist = to_float(waist, "Waist")
    sbp = to_float(sbp, "SBP")
    dbp = to_float(dbp, "DBP")
    chol = to_float(chol, "Cholesterol")
    hdl = to_float(hdl, "HDL")
    ldl = to_float(ldl, "LDL")
    trig = to_float(trig, "Triglyceride")
    creat = to_float(creat, "Creatinine")

    categorical_inputs = [
        urban_rural, sex, marital, education, work,
        history_diabetes, history_ht, history_renal,
        mental, smoking, risky_food, alcohol, activity
    ]

    numeric_inputs = [bmi, waist, sbp, dbp, chol, hdl, ldl, trig, creat]

    calculate = st.button(
        "Calculate Risk",
        disabled=any(v is None for v in categorical_inputs)
    )

# ---------------------------------------------------
# OUTPUT PANEL
# ---------------------------------------------------

with right:

    st.markdown("### 🚨 Risk Output")

    if calculate:

        # Validate numeric inputs
        if any(v is None for v in numeric_inputs):
            st.warning("Please complete all numerical inputs.")
            st.stop()

        if sbp < dbp:
            st.error("Invalid BP values")
            st.stop()

        # Initialize features
        features = {attr.name: 0 for attr in model.domain.attributes}

        # Numeric mapping
        numeric_map = {
            "BMI": bmi,
            "WaistCircumference": waist,
            "SystolicBloodPressure": sbp,
            "DiastolicBloodPressure": dbp,
            "TotalCholesterol": chol,
            "HDL": hdl,
            "LDL": ldl,
            "Trigliserid": trig,
            "Creatinin": creat
        }

        for k, v in numeric_map.items():
            if k in features:
                features[k] = v

        def safe_set(k):
            if k in features:
                features[k] = 1

        # Categorical mapping
        safe_set(f"Urban-Rural={urban_rural}")
        safe_set(f"Sex={sex}")
        safe_set(f"MaritalStatus={marital}")
        safe_set(f"EducationLevel={education}")

        if work == "Entrepreneur":
            safe_set("WorkStatus=Enterpreneur")
        else:
            safe_set(f"WorkStatus={work}")

        safe_set(f"HistoryDiabetes={history_diabetes}")
        safe_set(f"HistoryHypertension={history_ht}")
        safe_set(f"HistoryRenal={history_renal}")
        safe_set(f"MentalEmotionalDisorders={mental}")
        safe_set(f"Smoking={smoking}")
        safe_set(f"RiskyFoodConsumption={risky_food}")
        safe_set(f"AlcoholConsumption={alcohol}")
        safe_set(f"PhysicalActivityLEvel={activity}")

        # DataFrame
        df = pd.DataFrame([features])
        df = df.reindex(columns=[attr.name for attr in model.domain.attributes], fill_value=0)

        # Prediction
        try:
            orange_data = table_from_frame(df)
            pred = model(orange_data, model.Probs)
            risk = float(pred[0][1])
        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.stop()

        # Gauge
        option = {
            "series": [{
                "type": "gauge",
                "min": 0,
                "max": 100,
                "progress": {"show": True},
                "axisLine": {
                    "lineStyle": {
                        "width": 12,
                        "color": [
                            [0.15, "#2E8B57"],
                            [0.30, "#DAA520"],
                            [1.0, "#8B0000"]
                        ]
                    }
                },
                "detail": {"formatter": "{value}%"},
                "data": [{"value": round(risk * 100, 1)}]
            }]
        }

        st_echarts(option, height="450px")

        # Interpretation
        if risk >= 0.20:
            st.error("High Risk (>20%)")
        elif risk >= 0.10:
            st.warning("Moderate Risk (10-20%)")
        else:
            st.success("Low Risk (0-10%)")

# ---------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------

st.caption(
    "Disclaimer: This tool is for screening purposes only and does not replace clinical judgment."
)