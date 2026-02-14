"""
Customer Experience Analytics Dashboard
Interactive Streamlit dashboard for Ethiopian Bank Reviews Analysis

Design System:
- Primary: #1A73E8 (blue)
- Secondary: #0F172A (slate)
- Accent 1: #10B981 (green - positive)
- Accent 2: #F97316 (orange - alerts)
- Accent 3: #EF4444 (red - negative)
- Background: #F8FAFC (light)
- Cards: #FFFFFF
- Typography: Inter, IBM Plex Mono for numbers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# Color Palette
COLORS = {
    'primary': '#1A73E8',
    'secondary': '#0F172A',
    'positive': '#10B981',
    'negative': '#EF4444',
    'warning': '#F97316',
    'purple': '#8B5CF6',
    'neutral': '#94A3B8',
    'bg_light': '#F8FAFC',
    'bg_card': '#FFFFFF',
    'bg_secondary': '#EEF2F6',
    'text_primary': '#0F172A',
    'text_secondary': '#64748B',
    'grid': 'rgba(203, 213, 225, 0.3)'
}

# Page configuration
st.set_page_config(
    page_title="Bank Reviews Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Topography Design
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
    
    /* Main App Background */
    .stApp {{
        background-color: {COLORS['bg_light']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Main Container Padding */
    .block-container {{
        padding: 24px 48px 48px 48px;
        max-width: 1400px;
    }}
    
    /* Typography */
    h1 {{
        font-family: 'Inter', sans-serif;
        font-size: 32px !important;
        font-weight: 700 !important;
        color: {COLORS['secondary']} !important;
        margin-bottom: 8px !important;
    }}
    
    h2 {{
        font-family: 'Inter', sans-serif;
        font-size: 24px !important;
        font-weight: 600 !important;
        color: {COLORS['secondary']} !important;
        margin-top: 32px !important;
        margin-bottom: 16px !important;
    }}
    
    h3 {{
        font-family: 'Inter', sans-serif;
        font-size: 18px !important;
        font-weight: 600 !important;
        color: {COLORS['secondary']} !important;
    }}
    
    p, span, label {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: {COLORS['text_secondary']};
    }}
    
    /* KPI Card Styling */
    .kpi-card {{
        background: {COLORS['bg_card']};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid {COLORS['bg_secondary']};
        transition: all 0.2s ease;
    }}
    
    .kpi-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    .kpi-value {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 36px;
        font-weight: 600;
        color: {COLORS['secondary']};
        line-height: 1.2;
        margin-bottom: 4px;
    }}
    
    .kpi-label {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 500;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .kpi-change {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        margin-top: 8px;
    }}
    
    .kpi-change.positive {{
        color: {COLORS['positive']};
    }}
    
    .kpi-change.negative {{
        color: {COLORS['negative']};
    }}
    
    /* Chart Container */
    .chart-container {{
        background: {COLORS['bg_card']};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid {COLORS['bg_secondary']};
        margin-bottom: 24px;
    }}
    
    .chart-title {{
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: {COLORS['secondary']};
        margin-bottom: 16px;
    }}
    
    /* Insight Card */
    .insight-card {{
        background: {COLORS['bg_card']};
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid {COLORS['primary']};
        margin-bottom: 12px;
    }}
    
    .insight-card.positive {{
        border-left-color: {COLORS['positive']};
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.08) 0%, {COLORS['bg_card']} 100%);
    }}
    
    .insight-card.negative {{
        border-left-color: {COLORS['negative']};
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.08) 0%, {COLORS['bg_card']} 100%);
    }}
    
    .insight-title {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: {COLORS['secondary']};
        margin-bottom: 4px;
    }}
    
    .insight-text {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: {COLORS['text_secondary']};
    }}
    
    /* Review Card */
    .review-card {{
        background: {COLORS['bg_card']};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        border: 1px solid {COLORS['bg_secondary']};
        margin-bottom: 12px;
    }}
    
    .review-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    
    .review-bank {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 600;
        color: {COLORS['secondary']};
    }}
    
    .review-rating {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        color: {COLORS['warning']};
    }}
    
    .review-text {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: {COLORS['text_secondary']};
        line-height: 1.5;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: {COLORS['bg_card']} !important;
        border-right: 1px solid {COLORS['bg_secondary']};
        min-width: 300px !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        background: {COLORS['bg_card']} !important;
        padding-top: 2rem;
    }}
    
    [data-testid="stSidebar"] .block-container {{
        padding: 24px 16px;
    }}
    
    section[data-testid="stSidebar"] {{
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}
    
    /* Divider */
    .section-divider {{
        height: 1px;
        background: {COLORS['bg_secondary']};
        margin: 32px 0;
    }}
    
    /* Header Bar */
    .header-bar {{
        background: {COLORS['bg_card']};
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .header-title {{
        font-family: 'Inter', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['secondary']};
    }}
    
    .header-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: {COLORS['text_secondary']};
        margin-top: 4px;
    }}
    
    /* Badge */
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 500;
    }}
    
    .badge-positive {{
        background: rgba(16, 185, 129, 0.15);
        color: {COLORS['positive']};
    }}
    
    .badge-negative {{
        background: rgba(239, 68, 68, 0.15);
        color: {COLORS['negative']};
    }}
    
    .badge-neutral {{
        background: rgba(148, 163, 184, 0.15);
        color: {COLORS['neutral']};
    }}
    
    /* Streamlit Metric Override */
    [data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 32px !important;
        font-weight: 600 !important;
        color: {COLORS['secondary']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: {COLORS['text_secondary']} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    /* Selectbox & Input Styling */
    .stSelectbox > div > div {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['bg_secondary']};
        border-radius: 8px;
    }}
    
    .stSelectbox > div > div > div {{
        color: {COLORS['secondary']} !important;
    }}
    
    .stDateInput > div > div {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['bg_secondary']};
        border-radius: 8px;
    }}
    
    .stDateInput > div > div > input {{
        color: {COLORS['secondary']} !important;
    }}
    
    .stDateInput input {{
        color: {COLORS['secondary']} !important;
        -webkit-text-fill-color: {COLORS['secondary']} !important;
    }}
    
    [data-testid="stDateInput"] input {{
        color: {COLORS['secondary']} !important;
        -webkit-text-fill-color: {COLORS['secondary']} !important;
    }}
    
    .stMultiSelect > div > div {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['bg_secondary']};
        border-radius: 8px;
    }}
    
    .stMultiSelect > div > div > div {{
        color: {COLORS['secondary']} !important;
    }}
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] p {{
        color: {COLORS['secondary']} !important;
    }}
    
    [data-testid="stSidebar"] label {{
        color: {COLORS['secondary']} !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS['secondary']} !important;
    }}
    
    /* Fix all sidebar text */
    [data-testid="stSidebar"] span {{
        color: {COLORS['secondary']} !important;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    """Load data from CSV file."""
    # Get the path to the data file
    dashboard_dir = Path(__file__).parent
    project_root = dashboard_dir.parent
    
    # Try multiple possible locations for the CSV
    possible_paths = [
        dashboard_dir / 'data' / 'final.csv',  # dashboard/data/
        project_root / 'data' / 'processed' / 'final.csv',  # data/processed/
        project_root / 'data' / 'final.csv',  # data/
    ]
    
    csv_path = None
    for path in possible_paths:
        if path.exists():
            csv_path = path
            break
    
    if csv_path is None:
        st.error("❌ Data file not found! Please ensure '_final.csv' exists.")
        st.info("Expected locations: dashboard/data/ or data/processed/")
        st.stop()
    
    df = pd.read_csv(csv_path)
    
    # Convert date
    df['review_date'] = pd.to_datetime(df['review_date'])
    
    # Add bank_name if not present (map from bank column)
    if 'bank_name' not in df.columns and 'bank' in df.columns:
        bank_mapping = {
            'CBE': 'Commercial Bank of Ethiopia',
            'BOA': 'Bank of Abyssinia',
            'Dashen': 'Dashen Bank'
        }
        df['bank_name'] = df['bank'].map(bank_mapping)
    
    return df


def create_kpi_card(value, label, change=None, change_type="neutral"):
    """Create a styled KPI card."""
    change_html = ""
    if change:
        change_class = "positive" if change_type == "positive" else "negative" if change_type == "negative" else ""
        arrow = "↑" if change_type == "positive" else "↓" if change_type == "negative" else ""
        change_html = f'<div class="kpi-change {change_class}">{arrow} {change}</div>'
    
    return f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
            {change_html}
        </div>
    """


def create_chart_layout():
    """Return standard chart layout settings."""
    return dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color=COLORS['secondary']),
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(
            gridcolor=COLORS['grid'], 
            showgrid=True, 
            zeroline=False,
            tickfont=dict(color=COLORS['secondary']),
            title_font=dict(color=COLORS['secondary'])
        ),
        yaxis=dict(
            gridcolor=COLORS['grid'], 
            showgrid=True, 
            zeroline=False,
            tickfont=dict(color=COLORS['secondary']),
            title_font=dict(color=COLORS['secondary'])
        ),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=COLORS['secondary'])
        )
    )


def main():
    # Load data from CSV
    df = load_data()
    
    # Sidebar Filters
    st.sidebar.title("📊 Analytics")
    st.sidebar.caption("Filter & explore data")
    st.sidebar.divider()
    
    # Bank filter
    st.sidebar.markdown("**Select Bank**")
    banks = ['All Banks'] + list(df['bank_name'].unique())
    selected_bank = st.sidebar.selectbox("Bank", banks, label_visibility="collapsed")
    
    # Date range filter
    st.sidebar.markdown("**Date Range**")
    min_date = df['review_date'].min().date()
    max_date = df['review_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )
    
    # Sentiment filter
    st.sidebar.markdown("**Sentiment Filter**")
    sentiments = st.sidebar.multiselect(
        "Sentiment",
        ['POSITIVE', 'NEGATIVE'],
        default=['POSITIVE', 'NEGATIVE'],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    
    # Data summary
    st.sidebar.metric("Total Reviews", f"{len(df):,}")
    st.sidebar.caption(f"From {min_date} to {max_date}")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_bank != 'All Banks':
        filtered_df = filtered_df[filtered_df['bank_name'] == selected_bank]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['review_date'].dt.date >= date_range[0]) &
            (filtered_df['review_date'].dt.date <= date_range[1])
        ]
    
    if sentiments:
        filtered_df = filtered_df[filtered_df['sentiment_label_distilbert'].isin(sentiments)]
    
    # Header
    st.markdown(f"""
        <div class="header-bar">
            <div>
                <div class="header-title">Ethiopian Bank Reviews Analytics</div>
                <div class="header-subtitle">Customer Experience Insights Dashboard</div>
            </div>
            <div>
                <span class="badge badge-positive">Live Data</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    total_reviews = len(filtered_df)
    positive_reviews = len(filtered_df[filtered_df['sentiment_label_distilbert'] == 'POSITIVE'])
    negative_reviews = len(filtered_df[filtered_df['sentiment_label_distilbert'] == 'NEGATIVE'])
    satisfaction_rate = (positive_reviews / total_reviews * 100) if total_reviews > 0 else 0
    avg_rating = filtered_df['rating'].mean() if total_reviews > 0 else 0
    
    # KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card(
            f"{total_reviews:,}",
            "Total Reviews",
            "from Google Play",
            "neutral"
        ), unsafe_allow_html=True)
    
    with col2:
        change_type = "positive" if satisfaction_rate >= 50 else "negative"
        st.markdown(create_kpi_card(
            f"{satisfaction_rate:.1f}%",
            "Satisfaction Rate",
            f"{positive_reviews:,} positive",
            change_type
        ), unsafe_allow_html=True)
    
    with col3:
        change_type = "positive" if avg_rating >= 3.5 else "negative"
        st.markdown(create_kpi_card(
            f"{avg_rating:.2f}",
            "Average Rating",
            "out of 5 stars",
            change_type
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_kpi_card(
            f"{negative_reviews:,}",
            "Negative Reviews",
            f"{(negative_reviews/total_reviews*100):.1f}% of total" if total_reviews > 0 else "0%",
            "negative"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Charts Section - 60/40 split
    col_main, col_side = st.columns([3, 2])
    
    with col_main:
        # Sentiment Trend Over Time (Main Chart)
        st.markdown(f"""
            <div class="chart-container">
                <div class="chart-title">Satisfaction Trend Over Time</div>
            </div>
        """, unsafe_allow_html=True)
        
        df_time = filtered_df.copy()
        df_time['month'] = df_time['review_date'].dt.to_period('M').astype(str)
        
        monthly_sentiment = df_time.groupby(['month', 'bank_name']).apply(
            lambda x: (x['sentiment_label_distilbert'] == 'POSITIVE').mean() * 100
        ).reset_index(name='satisfaction_rate')
        
        fig = go.Figure()
        
        bank_colors = {
            'Commercial Bank of Ethiopia': COLORS['primary'],
            'Bank of Abyssinia': COLORS['warning'],
            'Dashen Bank': COLORS['positive']
        }
        
        for bank in monthly_sentiment['bank_name'].unique():
            bank_data = monthly_sentiment[monthly_sentiment['bank_name'] == bank]
            fig.add_trace(go.Scatter(
                x=bank_data['month'],
                y=bank_data['satisfaction_rate'],
                mode='lines+markers',
                name=bank,
                line=dict(width=3, color=bank_colors.get(bank, COLORS['neutral'])),
                marker=dict(size=8)
            ))
        
        fig.add_hline(y=50, line_dash="dash", line_color=COLORS['neutral'], 
                      annotation_text="50% Threshold", annotation_position="right")
        
        layout = create_chart_layout()
        layout.update(
            height=400,
            xaxis_title="Month",
            yaxis_title="Satisfaction Rate (%)",
            yaxis=dict(
                range=[0, 100], 
                gridcolor=COLORS['grid'], 
                showgrid=True, 
                zeroline=False,
                tickfont=dict(color=COLORS['secondary']),
                title_font=dict(color=COLORS['secondary'])
            ),
            hovermode='x unified'
        )
        fig.update_layout(**layout)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_side:
        # Bank Performance Comparison
        st.markdown(f"""
            <div class="chart-container">
                <div class="chart-title">Bank Performance</div>
            </div>
        """, unsafe_allow_html=True)
        
        avg_by_bank = df.groupby('bank_name').agg({
            'rating': 'mean',
            'review_id': 'count'
        }).reset_index()
        avg_by_bank.columns = ['bank_name', 'avg_rating', 'review_count']
        avg_by_bank = avg_by_bank.sort_values('avg_rating', ascending=True)
        
        colors = [COLORS['negative'] if r < 3 else COLORS['warning'] if r < 4 else COLORS['positive'] 
                  for r in avg_by_bank['avg_rating']]
        
        fig = go.Figure(go.Bar(
            x=avg_by_bank['avg_rating'],
            y=avg_by_bank['bank_name'],
            orientation='h',
            marker_color=colors,
            text=[f"{r:.2f} ⭐" for r in avg_by_bank['avg_rating']],
            textposition='outside',
            textfont=dict(family="IBM Plex Mono", size=14, color=COLORS['secondary'])
        ))
        
        layout = create_chart_layout()
        layout.update(
            height=300,
            xaxis=dict(
                range=[0, 5], 
                title="Average Rating", 
                gridcolor=COLORS['grid'], 
                showgrid=True, 
                zeroline=False,
                tickfont=dict(color=COLORS['secondary']),
                title_font=dict(color=COLORS['secondary'])
            ),
            yaxis_title="",
            showlegend=False
        )
        fig.update_layout(**layout)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Distribution Donut
        sentiment_counts = filtered_df['sentiment_label_distilbert'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.6,
            marker_colors=[COLORS['positive'] if l == 'POSITIVE' else COLORS['negative'] 
                          for l in sentiment_counts.index],
            textinfo='percent',
            textfont=dict(family="IBM Plex Mono", size=14, color='white')
        )])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12, color=COLORS['secondary']),
            margin=dict(l=40, r=40, t=40, b=40),
            height=250,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=COLORS['secondary'])),
            annotations=[dict(text='Sentiment', x=0.5, y=0.5, font_size=14, 
                            font_color=COLORS['secondary'], showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Rating Distribution Section
    st.markdown("## Rating Distribution by Bank")
    
    col1, col2, col3 = st.columns(3)
    
    rating_colors = ['#EF4444', '#F97316', '#FBBF24', '#84CC16', '#10B981']
    
    for idx, bank in enumerate(df['bank_name'].unique()):
        bank_df = df[df['bank_name'] == bank]
        rating_counts = bank_df['rating'].value_counts().sort_index()
        
        fig = go.Figure(go.Bar(
            x=rating_counts.index,
            y=rating_counts.values,
            marker_color=rating_colors,
            text=rating_counts.values,
            textposition='outside',
            textfont=dict(family="IBM Plex Mono", size=11, color=COLORS['text_secondary'])
        ))
        
        fig.update_layout(
            **create_chart_layout(),
            height=280,
            title=dict(text=bank, font=dict(size=14, color=COLORS['secondary'])),
            xaxis_title="Rating",
            yaxis_title="Count",
            showlegend=False
        )
        
        with [col1, col2, col3][idx]:
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Theme Analysis Section
    st.markdown("## Theme Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Theme distribution
        theme_counts = filtered_df['primary_theme'].value_counts().head(7)
        theme_counts = theme_counts[theme_counts.index != 'Other']
        
        fig = go.Figure(data=[go.Pie(
            labels=theme_counts.index,
            values=theme_counts.values,
            hole=0.5,
            marker_colors=px.colors.qualitative.Set2,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(family="Inter", size=11, color=COLORS['secondary'])
        )])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12, color=COLORS['secondary']),
            margin=dict(l=40, r=40, t=40, b=40),
            height=400,
            showlegend=False,
            annotations=[dict(text='Themes', x=0.5, y=0.5, font_size=16, 
                            font_color=COLORS['secondary'], showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pain Point Intensity
        theme_sentiment = []
        for theme in filtered_df['primary_theme'].dropna().unique():
            if theme == 'Other':
                continue
            theme_df = filtered_df[filtered_df['primary_theme'] == theme]
            if len(theme_df) >= 5:
                neg_pct = (theme_df['sentiment_label_distilbert'] == 'NEGATIVE').mean() * 100
                theme_sentiment.append({'theme': theme, 'negative_pct': neg_pct})
        
        if theme_sentiment:
            theme_sent_df = pd.DataFrame(theme_sentiment).sort_values('negative_pct', ascending=True)
            
            colors = [COLORS['positive'] if p < 40 else COLORS['warning'] if p < 60 else COLORS['negative'] 
                     for p in theme_sent_df['negative_pct']]
            
            fig = go.Figure(go.Bar(
                x=theme_sent_df['negative_pct'],
                y=theme_sent_df['theme'],
                orientation='h',
                marker_color=colors,
                text=[f"{p:.0f}%" for p in theme_sent_df['negative_pct']],
                textposition='outside',
                textfont=dict(family="IBM Plex Mono", size=12, color=COLORS['secondary'])
            ))
            
            layout = create_chart_layout()
            layout.update(
                height=400,
                title=dict(text="Pain Point Intensity (% Negative)", 
                          font=dict(size=14, color=COLORS['secondary'])),
                xaxis=dict(
                    range=[0, 100], 
                    title="Negative Review %", 
                    gridcolor=COLORS['grid'], 
                    showgrid=True, 
                    zeroline=False,
                    tickfont=dict(color=COLORS['secondary']),
                    title_font=dict(color=COLORS['secondary'])
                ),
                yaxis_title="",
                showlegend=False
            )
            fig.update_layout(**layout)
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Insights Section
    st.markdown("## Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Pain Points")
        neg_df = filtered_df[filtered_df['sentiment_label_distilbert'] == 'NEGATIVE']
        pain_points = neg_df['primary_theme'].value_counts().head(3)
        
        for theme, count in pain_points.items():
            if theme != 'Other':
                st.markdown(f"""
                    <div class="insight-card negative">
                        <div class="insight-title">❌ {theme}</div>
                        <div class="insight-text">{count:,} negative reviews identified</div>
                    </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Satisfaction Drivers")
        pos_df = filtered_df[filtered_df['sentiment_label_distilbert'] == 'POSITIVE']
        drivers = pos_df['primary_theme'].value_counts().head(3)
        
        for theme, count in drivers.items():
            if theme != 'Other':
                st.markdown(f"""
                    <div class="insight-card positive">
                        <div class="insight-title">✓ {theme}</div>
                        <div class="insight-text">{count:,} positive reviews identified</div>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Sample Reviews Section
    st.markdown("## Recent Reviews")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Positive Feedback")
        pos_samples = filtered_df[filtered_df['sentiment_label_distilbert'] == 'POSITIVE'].head(3)
        for _, row in pos_samples.iterrows():
            st.markdown(f"""
                <div class="review-card" style="border-left: 4px solid {COLORS['positive']};">
                    <div class="review-header">
                        <span class="review-bank">{row['bank_name']}</span>
                        <span class="review-rating">⭐ {row['rating']}</span>
                    </div>
                    <div class="review-text">{str(row['review_text'])[:180]}...</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Negative Feedback")
        neg_samples = filtered_df[filtered_df['sentiment_label_distilbert'] == 'NEGATIVE'].head(3)
        for _, row in neg_samples.iterrows():
            st.markdown(f"""
                <div class="review-card" style="border-left: 4px solid {COLORS['negative']};">
                    <div class="review-header">
                        <span class="review-bank">{row['bank_name']}</span>
                        <span class="review-rating">⭐ {row['rating']}</span>
                    </div>
                    <div class="review-text">{str(row['review_text'])[:180]}...</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 24px 0;">
            <p style="font-size: 14px; color: {COLORS['text_secondary']}; margin: 0;">
                Ethiopian Bank Reviews Analytics Dashboard
            </p>
            <p style="font-size: 12px; color: {COLORS['neutral']}; margin: 8px 0 0 0;">
                Data sourced from Google Play Store • Built with Streamlit & Plotly
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()