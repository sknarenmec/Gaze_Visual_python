import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import time

# Page configuration
st.set_page_config(
    page_title="GazeStudy Calibration",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'calibration_data' not in st.session_state:
    st.session_state.calibration_data = []
if 'gaze_data' not in st.session_state:
    st.session_state.gaze_data = []
if 'is_calibrated' not in st.session_state:
    st.session_state.is_calibrated = False
if 'current_point' not in st.session_state:
    st.session_state.current_point = 0
if 'subject_name' not in st.session_state:
    st.session_state.subject_name = "Test Subject"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E3B4E 0%, #4A5568 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .calibration-status {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .status-not-calibrated {
        background-color: #fee2e2;
        color: #dc2626;
        border: 2px solid #fca5a5;
    }
    
    .status-calibrating {
        background-color: #fef3c7;
        color: #d97706;
        border: 2px solid #fcd34d;
        animation: pulse 2s infinite;
    }
    
    .status-calibrated {
        background-color: #dcfce7;
        color: #16a34a;
        border: 2px solid #86efac;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #3b82f6;
    }
    
    .calibration-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Define calibration points (17 points as in original)
CALIBRATION_POINTS = [
    {"id": 1, "x": 10, "y": 10, "name": "Top-Left"},
    {"id": 2, "x": 50, "y": 10, "name": "Top-Center"},
    {"id": 3, "x": 90, "y": 10, "name": "Top-Right"},
    {"id": 4, "x": 10, "y": 30, "name": "Upper-Left"},
    {"id": 5, "x": 50, "y": 30, "name": "Upper-Center"},
    {"id": 6, "x": 90, "y": 30, "name": "Upper-Right"},
    {"id": 7, "x": 10, "y": 50, "name": "Center-Left"},
    {"id": 8, "x": 50, "y": 50, "name": "Center"},
    {"id": 9, "x": 90, "y": 50, "name": "Center-Right"},
    {"id": 10, "x": 10, "y": 70, "name": "Lower-Left"},
    {"id": 11, "x": 50, "y": 70, "name": "Lower-Center"},
    {"id": 12, "x": 90, "y": 70, "name": "Lower-Right"},
    {"id": 13, "x": 10, "y": 90, "name": "Bottom-Left"},
    {"id": 14, "x": 50, "y": 90, "name": "Bottom-Center"},
    {"id": 15, "x": 90, "y": 90, "name": "Bottom-Right"},
    {"id": 16, "x": 30, "y": 20, "name": "Extra Point 1"},
    {"id": 17, "x": 70, "y": 80, "name": "Extra Point 2"},
]

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>👁️ GazeStudy Calibration System</h1>
            <p>Python-powered Eye Tracking Calibration Interface</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎮 Controls")
        
        # Subject information
        st.session_state.subject_name = st.text_input(
            "Subject Name", 
            value=st.session_state.subject_name
        )
        
        st.markdown("---")
        
        # Calibration controls
        st.subheader("🎯 Calibration")
        
        if st.button("🚀 Start Calibration", use_container_width=True):
            start_calibration()
        
        if st.button("🔄 Restart Calibration", use_container_width=True):
            restart_calibration()
        
        st.markdown("---")
        
        # Study controls
        st.subheader("📊 Study")
        
        if st.button("▶️ Start Study", use_container_width=True, disabled=not st.session_state.is_calibrated):
            start_study()
        
        if st.button("📥 Export Data", use_container_width=True):
            export_data()
        
        st.markdown("---")
        
        # Simulation controls
        st.subheader("🎲 Simulation")
        if st.button("Generate Sample Gaze Data", use_container_width=True):
            generate_sample_gaze_data()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_calibration_status()
        display_calibration_interface()
    
    with col2:
        display_statistics()
        display_data_preview()

def display_calibration_status():
    """Display current calibration status"""
    if not st.session_state.is_calibrated and st.session_state.current_point == 0:
        status_class = "status-not-calibrated"
        status_text = "❌ Not Calibrated"
        message = "Click 'Start Calibration' to begin"
    elif not st.session_state.is_calibrated and st.session_state.current_point > 0:
        status_class = "status-calibrating"
        status_text = f"🔄 Calibrating... ({st.session_state.current_point}/17)"
        message = f"Continue clicking calibration points"
    else:
        status_class = "status-calibrated"
        status_text = "✅ Calibrated"
        message = "Ready for study!"
    
    st.markdown(f"""
        <div class="calibration-status {status_class}">
            <h2>{status_text}</h2>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)

def display_calibration_interface():
    """Display the calibration point interface"""
    st.subheader("🎯 Calibration Points")
    
    if st.session_state.current_point == 0 and not st.session_state.is_calibrated:
        st.info("👆 Start calibration to see clickable calibration points")
        
        # Show calibration point layout preview
        fig = create_calibration_preview()
        st.plotly_chart(fig, use_container_width=True)
    
    elif st.session_state.current_point > 0 and not st.session_state.is_calibrated:
        display_active_calibration()
    
    else:
        st.success("✅ Calibration completed! Ready to start study.")
        
        # Show calibration results
        if st.session_state.calibration_data:
            fig = create_calibration_results()
            st.plotly_chart(fig, use_container_width=True)

def create_calibration_preview():
    """Create a preview of calibration point positions"""
    fig = go.Figure()
    
    for point in CALIBRATION_POINTS:
        fig.add_trace(go.Scatter(
            x=[point["x"]],
            y=[100 - point["y"]],  # Flip Y axis for display
            mode='markers+text',
            marker=dict(size=20, color='red', symbol='circle'),
            text=[f"P{point['id']}"],
            textposition="middle center",
            textfont=dict(color='white', size=10),
            name=point["name"],
            hovertemplate=f"<b>{point['name']}</b><br>Position: ({point['x']}%, {point['y']}%)<extra></extra>"
        ))
    
    fig.update_layout(
        title="Calibration Point Layout Preview",
        xaxis_title="Screen Width (%)",
        yaxis_title="Screen Height (%)",
        xaxis=dict(range=[0, 100], showgrid=True),
        yaxis=dict(range=[0, 100], showgrid=True),
        showlegend=False,
        height=400
    )
    
    return fig

def display_active_calibration():
    """Display active calibration interface"""
    current_point_data = CALIBRATION_POINTS[st.session_state.current_point - 1]
    
    st.write(f"**Current Point:** {current_point_data['name']}")
    st.write(f"**Position:** {current_point_data['x']}% x {current_point_data['y']}%")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            f"📍 Click Point {current_point_data['id']}: {current_point_data['name']}", 
            use_container_width=True,
            help=f"Click to calibrate point at position ({current_point_data['x']}%, {current_point_data['y']}%)"
        ):
            record_calibration_point(current_point_data)

def record_calibration_point(point_data):
    """Record a calibration point click"""
    # Simulate gaze data with some noise
    gaze_x = point_data["x"] + np.random.normal(0, 2)  # Add noise
    gaze_y = point_data["y"] + np.random.normal(0, 2)
    
    calibration_record = {
        "point_id": point_data["id"],
        "point_name": point_data["name"],
        "target_x": point_data["x"],
        "target_y": point_data["y"],
        "gaze_x": gaze_x,
        "gaze_y": gaze_y,
        "timestamp": datetime.now().isoformat(),
        "subject": st.session_state.subject_name
    }
    
    st.session_state.calibration_data.append(calibration_record)
    st.session_state.current_point += 1
    
    if st.session_state.current_point > len(CALIBRATION_POINTS):
        st.session_state.is_calibrated = True
        st.success("🎉 Calibration completed successfully!")
        st.balloons()
    else:
        st.success(f"✅ Point {point_data['id']} calibrated!")
    
    st.rerun()

def create_calibration_results():
    """Create visualization of calibration results"""
    df = pd.DataFrame(st.session_state.calibration_data)
    
    fig = go.Figure()
    
    # Target points
    fig.add_trace(go.Scatter(
        x=df['target_x'],
        y=100 - df['target_y'],  # Flip Y axis
        mode='markers',
        marker=dict(size=15, color='red', symbol='x'),
        name='Target Points',
        hovertemplate="<b>Target</b><br>X: %{x}%<br>Y: %{customdata}%<extra></extra>",
        customdata=df['target_y']
    ))
    
    # Gaze points
    fig.add_trace(go.Scatter(
        x=df['gaze_x'],
        y=100 - df['gaze_y'],  # Flip Y axis
        mode='markers',
        marker=dict(size=10, color='blue', symbol='circle'),
        name='Gaze Points',
        hovertemplate="<b>Gaze</b><br>X: %{x:.1f}%<br>Y: %{customdata:.1f}%<extra></extra>",
        customdata=df['gaze_y']
    ))
    
    # Connect corresponding points
    for i in range(len(df)):
        fig.add_trace(go.Scatter(
            x=[df.iloc[i]['target_x'], df.iloc[i]['gaze_x']],
            y=[100 - df.iloc[i]['target_y'], 100 - df.iloc[i]['gaze_y']],
            mode='lines',
            line=dict(color='gray', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title="Calibration Results: Target vs Gaze Points",
        xaxis_title="Screen Width (%)",
        yaxis_title="Screen Height (%)",
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    return fig

def display_statistics():
    """Display calibration and gaze statistics"""
    st.subheader("📊 Statistics")
    
    # Calibration stats
    if st.session_state.calibration_data:
        df = pd.DataFrame(st.session_state.calibration_data)
        
        # Calculate accuracy
        df['error_x'] = abs(df['target_x'] - df['gaze_x'])
        df['error_y'] = abs(df['target_y'] - df['gaze_y'])
        df['total_error'] = np.sqrt(df['error_x']**2 + df['error_y']**2)
        
        avg_error = df['total_error'].mean()
        
        st.metric(
            label="Average Error",
            value=f"{avg_error:.2f}%",
            help="Lower is better"
        )
        
        st.metric(
            label="Calibration Points",
            value=f"{len(df)}/17"
        )
        
        accuracy_score = max(0, 100 - (avg_error * 10))
        st.metric(
            label="Accuracy Score",
            value=f"{accuracy_score:.1f}/100"
        )
    
    # Gaze data stats
    if st.session_state.gaze_data:
        st.metric(
            label="Gaze Data Points",
            value=len(st.session_state.gaze_data)
        )

def display_data_preview():
    """Display preview of collected data"""
    st.subheader("📋 Data Preview")
    
    tab1, tab2 = st.tabs(["Calibration", "Gaze Data"])
    
    with tab1:
        if st.session_state.calibration_data:
            df = pd.DataFrame(st.session_state.calibration_data)
            st.dataframe(df[['point_name', 'target_x', 'target_y', 'gaze_x', 'gaze_y']], use_container_width=True)
        else:
            st.info("No calibration data yet")
    
    with tab2:
        if st.session_state.gaze_data:
            df = pd.DataFrame(st.session_state.gaze_data)
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("No gaze data yet")

def start_calibration():
    """Start the calibration process"""
    st.session_state.calibration_data = []
    st.session_state.current_point = 1
    st.session_state.is_calibrated = False
    st.success("🚀 Calibration started! Click the calibration points in order.")
    st.rerun()

def restart_calibration():
    """Restart calibration from beginning"""
    st.session_state.calibration_data = []
    st.session_state.gaze_data = []
    st.session_state.current_point = 0
    st.session_state.is_calibrated = False
    st.info("🔄 Calibration restarted. Click 'Start Calibration' to begin.")
    st.rerun()

def start_study():
    """Start the main study"""
    if not st.session_state.is_calibrated:
        st.error("❌ Please complete calibration first!")
        return
    
    st.success("🎬 Study started! (In a real implementation, this would redirect to the study interface)")
    
    # Log study start
    study_data = {
        "subject": st.session_state.subject_name,
        "study_start_time": datetime.now().isoformat(),
        "calibration_points": len(st.session_state.calibration_data),
        "status": "started"
    }
    
    st.json(study_data)

def generate_sample_gaze_data():
    """Generate sample gaze data for demonstration"""
    sample_points = []
    for i in range(100):
        sample_points.append({
            "x": np.random.uniform(0, 100),
            "y": np.random.uniform(0, 100),
            "timestamp": datetime.now().isoformat(),
            "confidence": np.random.uniform(0.7, 1.0)
        })
    
    st.session_state.gaze_data.extend(sample_points)
    st.success(f"✅ Generated {len(sample_points)} sample gaze data points!")
    st.rerun()

def export_data():
    """Export all collected data"""
    export_data = {
        "subject_name": st.session_state.subject_name,
        "export_timestamp": datetime.now().isoformat(),
        "calibration_data": st.session_state.calibration_data,
        "gaze_data": st.session_state.gaze_data,
        "is_calibrated": st.session_state.is_calibrated,
        "total_calibration_points": len(st.session_state.calibration_data),
        "total_gaze_points": len(st.session_state.gaze_data)
    }
    
    # Convert to JSON string
    json_string = json.dumps(export_data, indent=2)
    
    # Create download button
    st.download_button(
        label="📥 Download Data (JSON)",
        data=json_string,
        file_name=f"gaze_study_data_{st.session_state.subject_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    
    st.success("📊 Data ready for download!")

if __name__ == "__main__":
    main()
