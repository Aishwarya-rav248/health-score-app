import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Session State for Navigation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.set_page_config(page_title="Health Score App", layout='wide')

# -----------------------------
# Login Page
if not st.session_state.logged_in:
    st.title("Login")
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input('Patient ID')
        last_name = st.text_input('Last Name')
        dob = st.date_input('DOB')
    
    with col2:
        first_name = st.text_input('First Name')
        gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
    
    if st.button('Submit'):
        st.session_state.logged_in = True
        st.session_state.patient_id = patient_id
        st.session_state.name = first_name + " " + last_name
        st.rerun()

# -----------------------------
# Dashboard Page
else:
    st.title(f"Welcome {st.session_state.name}")
    st.subheader("Enter Health Metrics")

    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input('Weight (kg)', 30, 200)
        height = st.number_input('Height (cm)', 100, 250)
        bmi_manual = st.number_input('BMI (optional)', 10.0, 50.0, step=0.1)
        smoking = st.selectbox('Smoking', ['No', 'Yes'])
        
    with col2:
        bp = st.number_input('Blood Pressure (mm Hg)', 80, 200)
        heart_rate = st.number_input('Heart Rate (bpm)', 40, 180)
    
    # Calculate BMI
    if bmi_manual > 10:
        bmi = bmi_manual
    elif height > 0:
        bmi = weight / ((height/100)**2)
    else:
        bmi = None
    
    st.write(f"**Calculated BMI:** {bmi:.2f}")
    
    # ----------------------------
    # Health Score Calculation
    score = 100
    
    if bmi:
        if bmi > 30 or bmi < 18:
            score -= 10
    
    if bp > 140:
        score -= 10
        
    if heart_rate > 100:
        score -= 5
        
    if smoking == 'Yes':
        score -= 5
    
    # ----------------------------
    # Health Score Gauge Visualization
    st.subheader("Health Score")
    
    gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': "green" if score >= 80 else "orange" if score >=50 else "red"},
                 'steps': [
                     {'range': [0, 49], 'color': "red"},
                     {'range': [50, 79], 'color': "orange"},
                     {'range': [80, 100], 'color': "green"}
                 ]},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    st.plotly_chart(gauge)
    
    if score >= 80:
        st.success("Excellent")
    elif score >= 50:
        st.warning("Needs Improvement")
    else:
        st.error("Unhealthy: Immediate Action Required!")
    
    # ----------------------------
    # Preventive Measures
    st.subheader("Preventive Measures")
    
    if bmi:
        st.write(f"1. BMI Optimization (BMI: {bmi:.2f}) – Focus on balanced diet & exercise.")
    if heart_rate > 80:
        st.write(f"2. Heart Rate Management ({heart_rate} bpm) – Stress reduction techniques.")
    st.write("3. Regular Monitoring – Track BP, cholesterol, glucose levels.")
    
    # ----------------------------
    # Back Button to Login
    if st.button('Back to Login'):
        st.session_state.logged_in = False
        st.rerun()

