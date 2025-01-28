import streamlit as st
import requests
import time
import pandas as pd
import json

# SnapLogic API details
URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/Aleksandra%20Kulawska/data_validator/data_validator_api"
BEARER_TOKEN = "qxQ1ovugVyLvt1GWahQO88iyHY9cgH4J"
timeout = 300

def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

# Title and description
st.markdown(
    """
    <h1 style="
        color: #0066B3;
        margin-bottom: 0.2em;">
        Data Validation Assistant
    </h1>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        margin: 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <p style="
            color: #424245;
            font-size: 0.95em;
            margin: 0 0 15px 0;">Instantly analyze your CSV files against industry standards and receive detailed validation reports with actionable insights.</p>
        <ul style="
            margin-bottom: 0;
            color: #424245;
            font-size: 0.95em;
            padding-left: 20px;">
            <li>🔍 Preview your data structure</li>
            <li>✅ Get comprehensive validation results</li>
            <li>💡 Receive actionable recommendations</li>
        </ul>
        <p style="
            color: #424245;
            font-size: 0.95em;
            margin: 15px 0 0 0;
            font-style: italic;">Upload your sample data file to begin.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# File uploader
st.markdown(
    """
    <div style="height: 20px"></div>
    """, 
    unsafe_allow_html=True
)

st.markdown("##### Upload Data File")

customer_file = st.file_uploader(
    "Upload Sample Data (CSV/TXT)", 
    type=["csv", "txt"], 
    key="data",
    help="Upload your data file for validation"
)

# Add file preview section
if customer_file is not None:
    with st.spinner('Previewing file...'):
        try:
            df = pd.read_csv(
                customer_file,
                on_bad_lines='warn',
                engine='python',
                quoting=3
            )
            customer_file.seek(0)
            
            st.write("### File Preview:")
            st.write(f"Total rows: {len(df)}")
            st.dataframe(df.head(5), use_container_width=True)
        except Exception as e:
            st.error(f"Error previewing file: {str(e)}")
            st.info("Note: Your file may contain inconsistent formatting. The validation process will still continue.")

def display_status_box(status):
    status = status.upper()
    status_styles = {
        "RED": {"color": "#842029", "bg": "#f8d7da", "border": "#f5c2c7", "emoji": "🔴"},
        "YELLOW": {"color": "#664d03", "bg": "#fff3cd", "border": "#ffecb5", "emoji": "🟡"},
        "GREEN": {"color": "#0f5132", "bg": "#d1e7dd", "border": "#badbcc", "emoji": "🟢"}
    }
    style = status_styles.get(status, status_styles["RED"])
    
    st.markdown(
        f"""
        <div style="
            padding: 16px 20px;
            border-radius: 8px;
            margin: 25px 0;
            background-color: {style['bg']};
            border: 1px solid {style['border']};
            color: {style['color']};
            font-weight: 500;
            display: flex;
            align-items: center;
        ">
            <span style="font-size: 20px; margin-right: 10px;">{style['emoji']}</span>
            <span>Validation Status: {status}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_section(title, content, icon):
    if not content:  # Skip empty sections
        return
        
    st.markdown(
        f"""
        <div style="margin-top: 15px;">
            <div style="
                padding: 12px 16px;
                background-color: #f8f9fa;
                border-left: 4px solid #0d6efd;
                font-weight: 500;
                border-radius: 0 4px 4px 0;
                display: flex;
                align-items: center;
            ">
                <span style="margin-right: 8px;">{icon}</span>
                {title}
            </div>
            <div style="
                margin: 8px 0 0 20px;
                line-height: 1.6;
                padding: 8px 16px;
            ">
                {('<br>'.join([f"• {item}" for item in content]) if isinstance(content, list) else content)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if st.button("Run Validation"):
    if not customer_file:
        st.error("Please upload the customer data file before running the validation.")
    else:
        with st.spinner('Processing validation request...'):
            try:
                response = requests.post(
                    url=URL,
                    data=customer_file.getvalue(),
                    headers={
                        "Authorization": f"Bearer {BEARER_TOKEN}",
                        "Content-Type": "text/csv"
                    },
                    timeout=timeout
                )

                if response.status_code == 200:
                    try:
                        result = response.json()

                        if result and isinstance(result, list) and len(result) > 0:
                            # Extract the json_output from the response
                            validation_data = result[0].get('json_output', {})
                            
                            if validation_data:
                                # Display validation status
                                display_status_box(validation_data.get('validation_status', 'RED'))
                                
                                # Display other sections with icons
                                if validation_data.get('errors'):
                                    display_section("Errors", validation_data['errors'], "⛔")
                                    
                                if validation_data.get('warnings'):
                                    display_section("Warnings", validation_data['warnings'], "⚠️")
                                    
                                if validation_data.get('recommendations'):
                                    display_section("Recommendations", validation_data['recommendations'], "💡")
                                    
                                if validation_data.get('conclusion'):
                                    display_section("Conclusion", validation_data['conclusion'], "📝")
                            else:
                                st.error("No validation data found in the response")
                        else:
                            st.error("Invalid response format")
                            
                    except json.JSONDecodeError:
                        st.error("Failed to parse API response")
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)}")