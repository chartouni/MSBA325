import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Lebanese Immigration Dashboard",
    page_icon="🇱🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #ff6b6b;
        padding-left: 1rem;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the immigration data"""
    try:
        # You'll need to update this path to your actual file
        df = pd.read_csv('leb immigrants.csv')
        
        # Convert numeric columns to proper dtypes
        numeric_cols = ['Number of Bangladeshi', 'Number of Sri Lankan', 'Number of Sudanese',
                        'Number of Egyptian', 'Number of Ethiopians', 'Number of Iraqi']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Extract district and governorate names
        df['District'] = df['District URI'].str.split('/').str[-1].str.replace('_', ' ')
        df['Governorate'] = df['Governorate URI'].str.split('/').str[-1].str.replace('_', ' ')
        
        # Calculate total immigrants per district
        df['Total_Immigrants'] = df[numeric_cols].sum(axis=1)
        
        return df, numeric_cols
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'leb immigrants.csv' is in your app directory.")
        return None, None

def create_stacked_bar_chart(df, numeric_cols, top_n, selected_nationalities):
    """Create interactive stacked bar chart"""
    top_districts = df.nlargest(top_n, 'Total_Immigrants')
    
    # Filter columns based on selection
    cols_to_show = [col for col in numeric_cols if col.replace('Number of ', '') in selected_nationalities]
    
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for i, col in enumerate(cols_to_show):
        if col in df.columns:
            fig.add_trace(go.Bar(
                name=col.replace('Number of ', ''),
                x=top_districts['District'],
                y=top_districts[col],
                marker_color=colors[i % len(colors)],
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'District: %{x}<br>' +
                             'Count: %{y}<br>' +
                             '<extra></extra>'
            ))
    
    fig.update_layout(
        title=f'Immigration Composition by District (Top {top_n})',
        barmode='stack',
        xaxis_title='District',
        yaxis_title='Number of Immigrants',
        xaxis_tickangle=45,
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_governorate_analysis(df, numeric_cols, chart_type):
    """Create governorate-level analysis"""
    gov_data = df.groupby('Governorate')[numeric_cols].sum().reset_index()
    gov_data['Total'] = gov_data[numeric_cols].sum(axis=1)
    gov_data = gov_data.sort_values('Total', ascending=False)
    
    if chart_type == "Horizontal Bar":
        fig = px.bar(gov_data.sort_values('Total', ascending=True),
                     x='Total',
                     y='Governorate',
                     orientation='h',
                     title='Total Immigration by Governorate',
                     color='Total',
                     color_continuous_scale='viridis')
    else:  # Pie Chart
        fig = px.pie(gov_data,
                     values='Total',
                     names='Governorate',
                     title='Immigration Distribution by Governorate')
    
    fig.update_layout(height=500)
    return fig

def main():
    # Load data
    df, numeric_cols = load_data()
    
    if df is None:
        st.stop()
    
    # Main header
    st.markdown('<h1 class="main-header">🇱🇧 Lebanese Immigration Dashboard</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class="insight-box">
    <h3>📊 Dashboard Overview</h3>
    <p>This interactive dashboard analyzes immigration patterns across Lebanese districts and governorates. 
    Explore data from six major immigrant populations: Bangladeshi, Sri Lankan, Sudanese, Egyptian, Ethiopian, and Iraqi communities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_immigrants = df['Total_Immigrants'].sum()
        st.markdown(f"""
        <div class="metric-container">
        <h3>👥 Total Immigrants</h3>
        <h2 style="color: #ff6b6b;">{total_immigrants:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        districts_with_immigrants = (df['Total_Immigrants'] > 0).sum()
        st.markdown(f"""
        <div class="metric-container">
        <h3>🏘️ Active Districts</h3>
        <h2 style="color: #4ecdc4;">{districts_with_immigrants}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        top_district = df.loc[df['Total_Immigrants'].idxmax(), 'District']
        top_count = df['Total_Immigrants'].max()
        st.markdown(f"""
        <div class="metric-container">
        <h3>🎯 Top District</h3>
        <h4 style="color: #45b7d1;">{top_district}</h4>
        <p>({top_count:,} immigrants)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Most common nationality
        nationality_totals = {}
        for col in numeric_cols:
            total = df[col].sum()
            if total > 0:
                nationality_totals[col.replace('Number of ', '')] = total
        top_nationality = max(nationality_totals, key=nationality_totals.get)
        st.markdown(f"""
        <div class="metric-container">
        <h3>🌍 Largest Group</h3>
        <h4 style="color: #96ceb4;">{top_nationality}</h4>
        <p>({nationality_totals[top_nationality]:,} people)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("🎛️ Interactive Controls")
    
    # Control 1: Number of top districts to show
    top_n = st.sidebar.slider(
        "Number of Top Districts to Display",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        help="Adjust how many top districts to show in the stacked bar chart"
    )
    
    # Control 2: Nationality selection
    all_nationalities = [col.replace('Number of ', '') for col in numeric_cols]
    selected_nationalities = st.sidebar.multiselect(
        "Select Nationalities to Display",
        options=all_nationalities,
        default=all_nationalities,
        help="Choose which immigrant populations to include in the analysis"
    )
    
    # Visualization 1: District-level Stacked Bar Chart
    st.markdown('<h2 class="sub-header">📊 Immigration by District</h2>', unsafe_allow_html=True)
    
    if selected_nationalities:
        fig1 = create_stacked_bar_chart(df, numeric_cols, top_n, selected_nationalities)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Insights for visualization 1
        filtered_cols = [col for col in numeric_cols if col.replace('Number of ', '') in selected_nationalities]
        top_district_data = df.nlargest(1, 'Total_Immigrants').iloc[0]
        
        st.markdown(f"""
        <div class="insight-box">
        <h4>💡 Key Insights - District Analysis</h4>
        <ul>
        <li><strong>{top_district_data['District']}</strong> has the highest concentration with {top_district_data['Total_Immigrants']:,} total immigrants</li>
        <li>Selected populations represent <strong>{sum(df[col].sum() for col in filtered_cols):,}</strong> immigrants across all districts</li>
        <li>The top {top_n} districts account for <strong>{df.nlargest(top_n, 'Total_Immigrants')['Total_Immigrants'].sum() / df['Total_Immigrants'].sum() * 100:.1f}%</strong> of total immigration</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please select at least one nationality to display the chart.")
    
    # Additional control for second visualization
    st.sidebar.markdown("---")
    chart_type = st.sidebar.selectbox(
        "Governorate Chart Type",
        options=["Horizontal Bar", "Pie Chart"],
        help="Choose how to display governorate-level data"
    )
    
    # Visualization 2: Governorate-level Analysis
    st.markdown('<h2 class="sub-header">🗺️ Immigration by Governorate</h2>', unsafe_allow_html=True)
    
    fig2 = create_governorate_analysis(df, numeric_cols, chart_type)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Insights for visualization 2
    gov_data = df.groupby('Governorate')[numeric_cols].sum().reset_index()
    gov_data['Total'] = gov_data[numeric_cols].sum(axis=1)
    gov_data = gov_data.sort_values('Total', ascending=False)
    top_gov = gov_data.iloc[0]
    
    st.markdown(f"""
    <div class="insight-box">
    <h4>💡 Key Insights - Governorate Analysis</h4>
    <ul>
    <li><strong>{top_gov['Governorate']}</strong> governorate leads with {top_gov['Total']:,} total immigrants</li>
    <li>Top 3 governorates account for <strong>{gov_data.head(3)['Total'].sum() / gov_data['Total'].sum() * 100:.1f}%</strong> of all immigrants</li>
    <li>Immigration is distributed across <strong>{len(gov_data[gov_data['Total'] > 0])}</strong> governorates</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional Analysis Section
    st.markdown('<h2 class="sub-header">🔍 Detailed Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Nationality distribution
        nationality_totals = {}
        for col in numeric_cols:
            total = df[col].sum()
            if total > 0:
                nationality_totals[col.replace('Number of ', '')] = total
        
        fig_pie = px.pie(values=list(nationality_totals.values()),
                        names=list(nationality_totals.keys()),
                        title="Overall Immigration Distribution by Nationality")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Top districts table
        st.subheader("Top 10 Districts by Immigration")
        top_districts_table = df.nlargest(10, 'Total_Immigrants')[['District', 'Governorate', 'Total_Immigrants']].reset_index(drop=True)
        top_districts_table.index += 1  # Start index from 1
        st.dataframe(top_districts_table, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
    <p>📊 Lebanese Immigration Dashboard | Built with Streamlit & Plotly</p>
    <p>Data visualization for immigration patterns across Lebanese districts and governorates</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
