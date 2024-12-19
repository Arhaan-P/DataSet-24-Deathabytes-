import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
# import google.generativeai as genai
import os

# Configure Gemini API
# def configure_genai():
#     genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'your-api-key-here'))
#     model = genai.GenerativeModel('gemini-pro')
#     return model

def create_database():
    conn = sqlite3.connect('system_reports.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  grid_voltage REAL,
                  grid_frequency REAL,
                  cooling_temp REAL,
                  cooling_humidity INTEGER,
                  file_integrity INTEGER,
                  error_count INTEGER,
                  cpu_usage INTEGER,
                  memory_usage INTEGER,
                  network_traffic REAL,
                  network_traffic_breach INTEGER,
                  firewall_alerts INTEGER,
                  status TEXT,
                  report_text TEXT)''')
    conn.commit()
    conn.close()

def generate_report_text(input_data, prediction):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""System Status Report - {timestamp}
    
Overall Status: {prediction}

Key Metrics:
- Grid Voltage: {input_data['Grid_Voltage']} V
- Grid Frequency: {input_data['Grid_Frequency']} Hz
- Cooling Temperature: {input_data['Cooling_Temperature']}°C
- CPU Usage: {input_data['CPU_Usage']}%
- Memory Usage: {input_data['Memory_Usage']}%

Alerts and Issues:
- Error Count: {input_data['Error_Count']}
- Firewall Alerts: {input_data['Firewall_Alerts']}
- Network Traffic Breach: {'Yes' if input_data['Network_Traffic_Breach'] == 1 else 'No'}

System Health Indicators:
- File Integrity: {'Pass' if input_data['File_Integrity'] == 1 else 'Fail'}
- Network Traffic: {input_data['Network_Traffic']} Mbps
"""
    return report

def save_report_to_db(input_data, prediction, report_text):
    conn = sqlite3.connect('system_reports.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO reports 
                 (timestamp, grid_voltage, grid_frequency, cooling_temp, 
                  cooling_humidity, file_integrity, error_count, cpu_usage,
                  memory_usage, network_traffic, network_traffic_breach,
                  firewall_alerts, status, report_text)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               input_data['Grid_Voltage'],
               input_data['Grid_Frequency'],
               input_data['Cooling_Temperature'],
               input_data['Cooling_Humidity'],
               input_data['File_Integrity'],
               input_data['Error_Count'],
               input_data['CPU_Usage'],
               input_data['Memory_Usage'],
               input_data['Network_Traffic'],
               input_data['Network_Traffic_Breach'],
               input_data['Firewall_Alerts'],
               prediction,
               report_text))
    
    conn.commit()
    conn.close()

def main():
    # Initialize database
    create_database()
    
    # Initialize Gemini
    # model = configure_genai()
    
    # Set page config
    st.set_page_config(page_title="System Status Predictor", layout="wide")
    
    # Create tabs
    tabs = st.tabs(["Prediction", "Report Generator", "Q&A"])
    
    # Store session state
    if 'current_input_data' not in st.session_state:
        st.session_state.current_input_data = None
    if 'current_prediction' not in st.session_state:
        st.session_state.current_prediction = None
    
    # Prediction Tab
    with tabs[0]:
        st.title("System Status Prediction")
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.header("Input Parameters")
            
            grid_voltage = st.number_input("Grid Voltage", min_value=0.0, max_value=500.0, value=220.0)
            grid_frequency = st.number_input("Grid Frequency (Hz)", min_value=0.0, max_value=100.0, value=50.0)
            cooling_temp = st.number_input("Cooling Temperature (°C)", min_value=0.0, max_value=100.0, value=25.0)
            cooling_humidity = st.slider("Cooling Humidity (%)", min_value=0, max_value=100, value=50)
            file_integrity = st.selectbox("File Integrity", options=[0, 1], format_func=lambda x: "Pass" if x == 1 else "Fail")
            error_count = st.number_input("Error Count", min_value=0, max_value=1000, value=0, step=1)
            cpu_usage = st.slider("CPU Usage (%)", min_value=0, max_value=100, value=50)
            memory_usage = st.slider("Memory Usage (%)", min_value=0, max_value=100, value=50)
            network_traffic = st.number_input("Network Traffic (Mbps)", min_value=0.0, max_value=10000.0, value=100.0)
            network_traffic_breach = st.selectbox("Network Traffic Breach", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            firewall_alerts = st.number_input("Firewall Alerts", min_value=0, max_value=1000, value=0, step=1)

        with right_col:
            st.header("Prediction Results")
            
            if st.button("Predict Status"):
                input_data = {
                    'Grid_Voltage': grid_voltage,
                    'Grid_Frequency': grid_frequency,
                    'Cooling_Temperature': cooling_temp,
                    'Cooling_Humidity': cooling_humidity,
                    'File_Integrity': file_integrity,
                    'Error_Count': error_count,
                    'CPU_Usage': cpu_usage,
                    'Memory_Usage': memory_usage,
                    'Network_Traffic': network_traffic,
                    'Network_Traffic_Breach': network_traffic_breach,
                    'Firewall_Alerts': firewall_alerts
                }
                
                # Store in session state
                st.session_state.current_input_data = input_data
                
                # Placeholder prediction logic
                prediction = "Normal" if all([
                    cpu_usage < 80,
                    memory_usage < 80,
                    error_count < 10,
                    network_traffic_breach == 0,
                    firewall_alerts < 5
                ]) else "Abnormal"
                
                st.session_state.current_prediction = prediction
                
                st.markdown("### System Status:")
                if prediction == "Normal":
                    st.success("NORMAL")
                else:
                    st.error("ABNORMAL")
                
                st.markdown("### Input Summary:")
                st.dataframe(pd.DataFrame([input_data]))
                
                if st.button("Generate Report"):
                    st.switch_page("Report Generator")
    
    # Report Generator Tab
    with tabs[1]:
        st.title("Report Generator")
        
        if st.session_state.current_input_data and st.session_state.current_prediction:
            report_text = generate_report_text(st.session_state.current_input_data, 
                                            st.session_state.current_prediction)
            
            st.text_area("Generated Report", report_text, height=400)
            
            if st.button("Save Report"):
                save_report_to_db(st.session_state.current_input_data,
                                st.session_state.current_prediction,
                                report_text)
                st.success("Report saved to database!")
            
            if st.button("Ask Questions"):
                st.switch_page("Q&A")
        else:
            st.warning("Please generate a prediction first!")
    
    # Q&A Tab
    with tabs[2]:
        st.title("Q&A System")
        
        user_question = st.text_input("Ask a question about the system status:")
        
        if user_question:
            if st.session_state.current_input_data and st.session_state.current_prediction:
                # Prepare context for Gemini
                context = f"""
                System Status: {st.session_state.current_prediction}
                Current Metrics: {st.session_state.current_input_data}
                Question: {user_question}
                """
                
                try:
                    response = model.generate_content(context)
                    st.text_area("Answer", response.text, height=200)
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
            else:
                st.warning("Please generate a prediction first!")

if __name__ == "__main__":
    main()