import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime
import json
import os

sys.path.insert(0, str(Path(__file__).parent))

from synthai.data.database import Database
from synthai.data.repositories.user_repository import UserRepository
from synthai.data.repositories.prediction_repository import PredictionRepository
from synthai.data.repositories.dataset_repository import DatasetRepository
from synthai.data.repositories.payment_repository import UsageLogRepository
from synthai.data.repositories.model_status_repository import ModelStatusRepository
from synthai.data.repositories.crop_data_repository import CropDataRepository
from synthai.business.recommendation.crop_recommender import CropRecommender
from synthai.business.rules.usage_limits import UsageLimits
from synthai.ai.preprocessing.data_loader import DataLoader
from synthai.ai.evaluation.metrics import DataStatistics
from synthai.services.training_service import TrainingService
from synthai.services.generation_service import GenerationService

st.set_page_config(
    page_title="SynthAI - Smart Agricultural Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Inter', sans-serif;}
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 100%);
        min-height: 100vh;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #E8F5E9 !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #81C784 !important;
    }
    
    .stApp > div:first-child {
        padding-top: 0rem !important;
    }
    
    .main-content {
        padding: 1rem 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #2E7D32;
    }
    .kpi-card .value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #2E7D32;
    }
    .kpi-card .label {
        font-size: 0.85rem;
        color: #666;
    }
    
    .feature-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .rec-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #2E7D32;
    }
    .rec-card .icon {
        width: 36px;
        height: 36px;
        background: #2E7D32;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1rem;
    }
    .rec-card .title {
        font-size: 0.75rem;
        color: #555;
    }
    .rec-card .value {
        font-size: 1rem;
        font-weight: 600;
        color: #1B5E20;
    }
    
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .stDataFrame {
        border-radius: 0.5rem;
    }
    
    .badge-valid {
        background: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
    }
    .badge-warning {
        background: #FF9800;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
    }
    .badge-invalid {
        background: #F44336;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
    }
    .badge-premium {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-free {
        background: #2E7D32;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
    }
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1B5E20;
        margin-bottom: 1rem;
    }
    
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'home'


def check_auth():
    if not st.session_state.logged_in:
        st.warning("Please login to access this page")
        st.stop()


def check_admin():
    check_auth()
    if st.session_state.user.get('role') != 'admin':
        st.warning("Access denied. Admin only.")
        st.stop()


def load_real_data() -> pd.DataFrame:
    loader = DataLoader("data/Crop_recommendation.csv")
    return loader.load()


def predict_crop_conditions(conditions: dict) -> pd.DataFrame:
    df = load_real_data()
    df['score'] = 0
    for col in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
        df['score'] += abs(df[col] - conditions.get(col, 50))
    df_sorted = df.sort_values('score').head(10)
    results = []
    for _, row in df_sorted.iterrows():
        results.append({
            'Crop': row['label'].title(),
            'Match Score': max(0, 100 - row['score']),
            'Temperature': round(row['temperature'], 2),
            'Humidity': round(row['humidity'], 2),
            'pH': round(row['ph'], 2),
            'Rainfall': round(row['rainfall'], 2)
        })
    return pd.DataFrame(results)


def plot_correlation(df: pd.DataFrame, title: str):
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return None
    corr = numeric_df.corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 9}
    ))
    fig.update_layout(title=title, height=350, margin=dict(l=40, r=40, t=40, b=40))
    return fig


def plot_distribution(real_df: pd.DataFrame, synth_df: pd.DataFrame, col: str):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=real_df[col], name='Real', marker_color='#2E7D32', opacity=0.7, histnorm='probability'))
    fig.add_trace(go.Histogram(x=synth_df[col], name='Synthetic', marker_color='#FF9800', opacity=0.7, histnorm='probability'))
    fig.update_layout(barmode='overlay', title=f'Distribution: {col}', height=300, template='plotly_white')
    return fig


def main():
    Database.init_db()
    init_session()
    render_sidebar()
    
    if not st.session_state.logged_in:
        show_login()
    else:
        user = st.session_state.user
        if user['role'] == 'admin':
            admin_routes = {
                'home': show_admin_home,
                'model': show_admin_model,
                'generate': show_admin_generate,
                'validate': show_admin_validation,
                'users': show_admin_users,
                'stats': show_admin_stats
            }
            page = st.session_state.get('page', 'home')
            admin_routes.get(page, show_admin_home)()
        else:
            farmer_routes = {
                'home': show_farmer_home,
                'crop_conditions': show_crop_conditions,
                'conditions_crop': show_conditions_crop,
                'history': show_history
            }
            page = st.session_state.get('page', 'home')
            farmer_routes.get(page, show_farmer_home)()


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0; color: #81C784;">SynthAI</h2>
            <p style="margin: 0; font-size: 0.8rem; color: #C8E6C9;">Smart Agricultural Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            user = st.session_state.user
            plan_badge = "badge-premium" if user['plan'] == 'premium' else "badge-free"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
                <div style="font-weight: 600;">{user['username']}</div>
                <div style="font-size: 0.75rem; opacity: 0.8;">{user['email']}</div>
                <span class="{plan_badge}" style="margin-top: 0.5rem; display: inline-block;">{user['plan'].upper()}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if user['role'] == 'admin':
                options = [
                    ('home', 'Home', 'fa-home'),
                    ('model', 'Train Model', 'fa-brain'),
                    ('generate', 'Generate Data', 'fa-database'),
                    ('validate', 'Validation', 'fa-check-circle'),
                    ('users', 'Users', 'fa-users'),
                    ('stats', 'Statistics', 'fa-chart-bar')
                ]
            else:
                options = [
                    ('home', 'Home', 'fa-home'),
                    ('crop_conditions', 'Crop → Conditions', 'fa-seedling'),
                    ('conditions_crop', 'Conditions → Crop', 'fa-search'),
                    ('history', 'History', 'fa-history')
                ]
            
            for page_id, label, _ in options:
                if st.button(label, key=page_id, use_container_width=True):
                    st.session_state.page = page_id
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.info("Please login to continue")


def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("###")
        st.markdown("###")
        st.markdown("## SynthAI")
        st.markdown("Smart Agricultural Intelligence Platform")
        
        st.markdown("---")
        st.markdown("### Sign In")
        
        login_user = st.text_input("Username")
        login_pass = st.text_input("Password", type="password")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            user = UserRepository.authenticate(login_user, Database.hash_password(login_pass))
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.page = 'home'
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.markdown("### Create Account")
        
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
        
        if st.button("Register", use_container_width=True):
            if reg_user and reg_email and reg_pass:
                if reg_pass != reg_pass2:
                    st.error("Passwords do not match")
                else:
                    user_id = UserRepository.create(reg_user, reg_email, Database.hash_password(reg_pass), "farmer")
                    if user_id is not None:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("Username or email already exists")
            else:
                st.warning("Please fill all fields")


def show_admin_home():
    users = UserRepository.find_all()
    
    st.markdown("# Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="value">{}</div>
            <div class="label">Total Users</div>
        </div>
        """.format(len(users)), unsafe_allow_html=True)
    
    with col2:
        status = ModelStatusRepository.get_status()
        trained = bool(status and status['is_trained'])
        st.markdown("""
        <div class="kpi-card">
            <div class="value">{}</div>
            <div class="label">Model Status</div>
        </div>
        """.format("Ready" if trained else "Not Ready"), unsafe_allow_html=True)
    
    with col3:
        df = load_real_data()
        st.markdown("""
        <div class="kpi-card">
            <div class="value">{:,}</div>
            <div class="label">Dataset Rows</div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col4:
        datasets = DatasetRepository.find_all()
        st.markdown("""
        <div class="kpi-card">
            <div class="value">{}</div>
            <div class="label">Datasets Generated</div>
        </div>
        """.format(len(datasets)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Quick Actions")
        
        if st.button("Train New Model", use_container_width=True):
            st.session_state.page = 'model'
            st.rerun()
        
        if st.button("Generate Synthetic Data", use_container_width=True):
            st.session_state.page = 'generate'
            st.rerun()
        
        if st.button("View Statistics", use_container_width=True):
            st.session_state.page = 'stats'
            st.rerun()
    
    with col2:
        st.markdown("### Recent Users")
        
        if users:
            user_data = [{"Username": u['username'], "Role": u['role'], "Plan": u['plan']} for u in users[-5:]]
            st.dataframe(pd.DataFrame(user_data), use_container_width=True)


def show_admin_model():
    st.markdown("# Train CTGAN Model")
    
    epochs = st.select_slider("Epochs", options=[50, 100, 200, 300, 500], value=300)
    
    if st.button("Train Model", type="primary"):
        with st.spinner("Training CTGAN..."):
            try:
                svc = TrainingService()
                svc.train(st.session_state.user['id'], epochs=epochs)
                
                Path("models").mkdir(exist_ok=True)
                st.success("Model trained successfully!")
            except Exception as e:
                st.error("Training failed: " + str(e))
    
    st.markdown("---")
    
    status = ModelStatusRepository.get_status()
    trained = bool(status and status['is_trained'])
    model_type = status['model_type'] if status else 'CTGAN'
    st.metric("Status", "Trained" if trained else "Not Trained")
    st.metric("Type", model_type)


def show_admin_generate():
    check_admin()
    
    st.markdown("# Generate Synthetic Data")
    
    num_rows = st.slider("Number of Rows", 100, 10000, 1000, step=100)
    
    if st.button("Generate", type="primary"):
        with st.spinner("Generating..."):
            try:
                result = GenerationService.generate(
                    user_id=st.session_state.user['id'],
                    num_rows=num_rows,
                )
                
                st.session_state.synthetic_df = result.get('preview')
                st.success("Generated " + str(result['rows']) + " rows!")
                
                synth_df = load_real_data().sample(n=min(num_rows, 100), replace=True).reset_index(drop=True)
                st.download_button(
                    "Download CSV",
                    synth_df.to_csv(index=False),
                    "synthetic_data.csv",
                    "text/csv"
                )
            except Exception as e:
                st.error("Generation failed: " + str(e))
    
    if st.session_state.get('synthetic_df') is not None:
        st.markdown("### Preview")
        preview = st.session_state.synthetic_df
        if isinstance(preview, list):
            st.dataframe(pd.DataFrame(preview).head(10))
        else:
            st.dataframe(load_real_data().head(10))


def show_admin_validation():
    check_admin()
    
    st.markdown("# Data Validation")
    
    datasets = DatasetRepository.find_all()
    
    st.markdown("### Generated Datasets")
    
    if datasets:
        for ds in datasets:
            st.markdown(f"""
            <div class="feature-card">
                <strong>Dataset #{ds['id']}</strong> - {ds['rows_generated']} rows
                <br><small>{ds['created_at']} by {ds.get('admin_username', 'unknown')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No datasets generated yet")
    
    st.markdown("---")
    st.markdown("### Validation Checks")
    
    real_df = load_real_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Real Data Validation")
        
        issues = []
        
        if real_df['ph'].min() < 0 or real_df['ph'].max() > 14:
            issues.append("pH out of range")
        if (real_df[['N', 'P', 'K']] < 0).any().any():
            issues.append("Negative nutrient values")
        
        if not issues:
            st.markdown('<span class="badge-valid">Valid</span>', unsafe_allow_html=True)
        else:
            for issue in issues:
                st.markdown('<span class="badge-warning">' + issue + '</span>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Statistics")
        
        st.markdown("**Mean values:**")
        st.write(real_df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].mean())
        
        st.markdown("**Correlation:**")
        fig = plot_correlation(real_df, "Real Data Correlation")
        if fig:
            st.plotly_chart(fig, use_container_width=True)


def show_admin_users():
    check_admin()
    
    st.markdown("# User Management")
    
    users = UserRepository.find_all()
    
    if users:
        user_data = [{"ID": u['id'], "Username": u['username'], "Email": u['email'],
                       "Role": u['role'], "Plan": u['plan'], "Created": u['created_at']} for u in users]
        st.dataframe(pd.DataFrame(user_data), use_container_width=True)
        
        st.markdown("### Update Subscription")
        
        col1, col2 = st.columns(2)
        
        with col1:
            usernames = [u['username'] for u in users if u['username'] != 'admin']
            target = st.selectbox("Select User", usernames if usernames else [''])
        with col2:
            new_plan = st.selectbox("New Plan", ["free", "premium"])
        
        if st.button("Update"):
            target_user = UserRepository.find_by_username(target)
            if target_user:
                UserRepository.update_plan(target_user['id'], new_plan)
                st.success("Updated!")
                st.rerun()
            else:
                st.error("User not found")


def show_admin_stats():
    check_admin()
    
    st.markdown("# Statistics")
    
    df = load_real_data()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", len(df))
    col2.metric("Features", len(df.columns))
    col3.metric("Crops", df['label'].nunique())
    col4.metric("Missing", df.isnull().sum().sum())
    
    st.markdown("### Dataset Preview")
    st.dataframe(df.head(10))
    
    st.markdown("### Statistics")
    st.dataframe(df.describe())


def show_farmer_home():
    user = st.session_state.user
    
    predictions_count = PredictionRepository.count_by_user(user['id'])
    usage_today = UsageLogRepository.count_today_by_action(user['id'], 'prediction')
    quota = UsageLimits.remaining_attempts(user['plan'], usage_today) if user['plan'] == 'free' else float('inf')
    
    st.markdown("# Welcome to SynthAI")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        badge = "badge-premium" if user['plan'] == 'premium' else "badge-free"
        st.markdown('<span class="' + badge + '">' + user['plan'].upper() + '</span>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Predictions", predictions_count)
    
    with col3:
        st.metric("Quota", str(quota) if quota != float('inf') else "Unlimited")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Crop → Conditions")
        
        if st.button("Start", use_container_width=True):
            st.session_state.page = 'crop_conditions'
            st.rerun()
    
    with col2:
        st.markdown("### Conditions → Crop")
        
        if st.button("Start", use_container_width=True):
            st.session_state.page = 'conditions_crop'
            st.rerun()


def show_crop_conditions():
    check_auth()
    
    user = st.session_state.user
    usage_today = UsageLogRepository.count_today_by_action(user['id'], 'prediction')
    can_use = user['plan'] == 'premium' or UsageLimits.can_attempt(user['plan'], user['role'], usage_today)
    
    if not can_use:
        st.warning("Daily quota reached. Upgrade to Premium.")
    
    recommender = CropRecommender(crop_df=CropDataRepository.load_all())
    crops = recommender.get_all_crops()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected = st.selectbox("Select Crop", crops)
    
    with col2:
        st.markdown("###")
        
        if st.button("Get Recommendations", type="primary", disabled=not can_use):
            if user['plan'] != 'premium':
                UsageLogRepository.add(user['id'], 'prediction', 1)
            
            rec = recommender.get_recommendation(selected)
            input_json = json.dumps({"crop": selected})
            output_json = json.dumps(rec)
            PredictionRepository.create(user['id'], "crop_conditions", input_json, output_json, crop_search=selected)
            
            st.session_state.current_rec = rec
    
    if 'current_rec' in st.session_state:
        rec = st.session_state.current_rec
        
        st.markdown("## " + rec['crop'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="rec-card"><div class="icon">T</div><div class="title">Temperature</div><div class="value">' + rec['optimal_temperature'] + '</div></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="rec-card"><div class="icon">H</div><div class="title">Humidity</div><div class="value">' + rec['optimal_humidity'] + '</div></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="rec-card"><div class="icon">p</div><div class="title">pH</div><div class="value">' + rec['optimal_ph'] + '</div></div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="rec-card"><div class="icon">R</div><div class="title">Rainfall</div><div class="value">' + rec['optimal_rainfall'] + '</div></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="rec-card"><div class="title">Water Level</div><div class="value">' + rec['water_level'] + '</div></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="rec-card"><div class="title">Fertilizer</div><div class="value">' + rec['fertilizer_level'] + '</div></div>', unsafe_allow_html=True)
        
        csv_data = pd.DataFrame([rec])
        st.download_button("Download", csv_data.to_csv(index=False), "recommendations.csv", "text/csv")


def show_conditions_crop():
    check_auth()
    
    user = st.session_state.user
    usage_today = UsageLogRepository.count_today_by_action(user['id'], 'prediction')
    can_use = user['plan'] == 'premium' or UsageLimits.can_attempt(user['plan'], user['role'], usage_today)
    
    if not can_use:
        st.warning("Daily quota reached.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_val = st.slider("Nitrogen (N)", 0, 140, 50)
        p_val = st.slider("Phosphorus (P)", 0, 145, 50)
        k_val = st.slider("Potassium (K)", 0, 205, 50)
    
    with col2:
        temp_val = st.slider("Temperature", 0, 50, 25)
        humidity_val = st.slider("Humidity", 0, 100, 70)
        ph_val = st.slider("pH", 0.0, 14.0, 6.5)
        rainfall_val = st.slider("Rainfall", 0, 500, 100)
    
    if st.button("Predict", type="primary", disabled=not can_use):
        if user['plan'] != 'premium':
            UsageLogRepository.add(user['id'], 'prediction', 1)
        
        conditions = {'N': n_val, 'P': p_val, 'K': k_val, 'temperature': temp_val, 'humidity': humidity_val, 'ph': ph_val, 'rainfall': rainfall_val}
        
        results = predict_crop_conditions(conditions)
        
        input_json = json.dumps(conditions)
        output_json = results.to_json(orient='records')
        PredictionRepository.create(user['id'], "conditions_crop", input_json, output_json)
        
        st.session_state.prediction_results = results
    
    if 'prediction_results' in st.session_state:
        results = st.session_state.prediction_results
        st.markdown("### Top Matches")
        st.dataframe(results)
        
        if not results.empty:
            top = results.iloc[0]
            st.success("Best: " + top['Crop'] + " (" + str(top['Match Score']) + "%)")


def show_history():
    check_auth()
    
    user = st.session_state.user
    
    st.markdown("# Prediction History")
    
    limit = 10 if user['plan'] == 'free' else 50
    
    predictions = PredictionRepository.find_by_user(user['id'], limit)
    
    st.metric("Total Predictions", len(predictions))
    
    if predictions:
        search = st.text_input("Search by crop")
        
        if search:
            predictions = PredictionRepository.search_by_crop(user['id'], search)
        
        if predictions:
            history_data = []
            for p in predictions:
                try:
                    input_data = json.loads(p['input_data'])
                    output_data = json.loads(p['output_result'])
                    
                    if isinstance(output_data, dict):
                        result = output_data.get('crop', 'N/A')
                    elif isinstance(output_data, list) and len(output_data) > 0:
                        result = output_data[0].get('Crop', 'N/A')
                    else:
                        result = str(output_data)[:50]
                    
                    history_data.append({
                        "Type": p['prediction_type'],
                        "Input": str(input_data)[:30],
                        "Result": result,
                        "Date": p['created_at']
                    })
                except:
                    history_data.append({
                        "Type": p['prediction_type'],
                        "Input": p['input_data'][:30],
                        "Result": p['output_result'][:30],
                        "Date": p['created_at']
                    })
            
            st.dataframe(pd.DataFrame(history_data), use_container_width=True)
        else:
            st.info("No predictions found")
    else:
        st.info("No prediction history yet")


if __name__ == "__main__":
    main()
