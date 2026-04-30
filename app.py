import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
# Sets the browser tab title and expands the layout to use the full screen width
st.set_page_config(page_title="Plot Twist Analytics", page_icon="🎬", layout="wide")

# --- 2. DATA SETUP & CACHING ---
@st.cache_data
def load_movie_data():
    """Loads and prepares the initial movie dataset."""
    raw_data = pd.read_csv("movies.csv")
    
    # Drop rows with missing values in critical columns
    clean_data = raw_data.dropna(subset=["year", "genre", "score", "budget", "gross", "votes", "runtime"])
    
    # Feature Engineering: Create a 'profit' column for business analysis
    clean_data['profit'] = clean_data['gross'] - clean_data['budget']
    
    return clean_data

movie_df = load_movie_data()

# --- 3. THE SIDEBAR (User Controls) ---
st.sidebar.title("🎬 Plot Twist Analytics")
st.sidebar.markdown("**Project Team:**")
st.sidebar.markdown("- Reynalen Leigh Alenzuela (Visuals)")
st.sidebar.markdown("- Gabriel Barabad (UI/UX Architect)")
st.sidebar.markdown("- Kirk Johnray Menez (Data Engineer)")
st.sidebar.markdown("---")

st.sidebar.header("Filter Options")
# Dynamic filters based on the dataset's actual min/max and unique values
selected_year = st.sidebar.slider("Release Year", int(movie_df['year'].min()), int(movie_df['year'].max()), 2010)
selected_genre = st.sidebar.selectbox("Movie Genre", movie_df['genre'].unique())

# Filter the dataframe based on user sidebar inputs
filtered_movies_df = movie_df[(movie_df['year'] == selected_year) & (movie_df['genre'] == selected_genre)]

# --- 4. MAIN DASHBOARD HEADER ---
st.title("🍿 The Movie Landscape Dashboard")
st.markdown("Exploring cinematic trends, profitability, and box office performances.")
st.markdown("---")

# --- 5. DYNAMIC KPIs & INSIGHTS ---
st.header(f"At a Glance: {selected_genre} Movies in {selected_year}")

# 5 Columns for top-level metric cards (Added ROI)
metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

# Pre-calculate ROI for the KPIs and the dynamic insight engine
avg_roi = 0
if not filtered_movies_df.empty and filtered_movies_df['budget'].mean() > 0:
    avg_roi = filtered_movies_df['gross'].mean() / filtered_movies_df['budget'].mean()

with metric_col1:
    st.metric("Total Movies Released", f"{len(filtered_movies_df)}")
with metric_col2:
    st.metric("Average IMDb Score", f"{filtered_movies_df['score'].mean():.1f}" if not filtered_movies_df.empty else "N/A")
with metric_col3:
    avg_budget_millions = filtered_movies_df['budget'].mean() / 1000000 if not filtered_movies_df.empty else 0
    st.metric("Average Budget", f"${avg_budget_millions:.1f}M")
with metric_col4:
    avg_gross_millions = filtered_movies_df['gross'].mean() / 1000000 if not filtered_movies_df.empty else 0
    st.metric("Average Gross Revenue", f"${avg_gross_millions:.1f}M")
with metric_col5:
    st.metric("Average ROI", f"{avg_roi:.2f}x")

st.markdown("---")

# --- 6. TABBED NAVIGATION LAYOUT ---
# Organizes the heavy charts into clean, clickable tabs
tab_financials, tab_correlations, tab_trends = st.tabs(["💰 Financials & Scores", "📊 Data Correlations", "📈 Historical Trends"])

# --- TAB 1: FINANCIALS & SCORES ---
with tab_financials:
    
    # --- NEW: TOP MOVIE SPOTLIGHT (The "Hero" Element) ---
    if not filtered_movies_df.empty:
        # Find the movie with the highest gross revenue in this filtered slice
        top_movie = filtered_movies_df.loc[filtered_movies_df['gross'].idxmax()]
        top_profit_m = top_movie['profit'] / 1000000
        st.info(f"🏆 **Box Office Champion ({selected_year}):** *{top_movie['name']}* generated **${top_profit_m:.1f}M** in net profit with an IMDb score of **{top_movie['score']}**.")
    else:
        st.warning("No movies found for this specific filter combination.")
        
    st.markdown("<br>", unsafe_allow_html=True) # Just a little spacing

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        yearly_release_volume = movie_df[movie_df['genre'] == selected_genre].groupby("year")["name"].count().reset_index()
        volume_line_chart = px.line(yearly_release_volume, x="year", y="name",
                                    title=f"Annual Release Volume ({selected_genre})",
                                    labels={"year": "Release Year", "name": "Number of Movies"})
        st.plotly_chart(volume_line_chart, use_container_width=True)

    with chart_col2:
        average_score_per_genre = movie_df[movie_df['year'] == selected_year].groupby("genre")["score"].mean().reset_index()
        score_bar_chart = px.bar(average_score_per_genre, x="genre", y="score",
                                 title=f"Average IMDb Score by Genre ({selected_year})", 
                                 color="genre",
                                 labels={"genre": "Movie Genre", "score": "IMDb Score"})
        st.plotly_chart(score_bar_chart, use_container_width=True)

    st.subheader("Budget vs. Gross Revenue")
    financial_scatter_plot = px.scatter(filtered_movies_df, x="budget", y="gross", size="votes", color="genre",
                                        hover_data=["name"],
                                        title=f"Financial Performance: {selected_genre} ({selected_year})",
                                        labels={"budget": "Production Budget ($)", "gross": "Gross Revenue ($)"})
    st.plotly_chart(financial_scatter_plot, use_container_width=True)

# --- TAB 2: CORRELATIONS ---
with tab_correlations:
    st.subheader("Feature Correlation Heatmap")
    st.markdown("Understanding the mathematical relationships between movie metrics.")
    
    # Isolate only the numeric columns so the correlation matrix doesn't break
    numeric_df = movie_df.select_dtypes(include=['float64', 'int64'])
    correlation_matrix = numeric_df.corr()
    
    correlation_heatmap = px.imshow(correlation_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")
    st.plotly_chart(correlation_heatmap, use_container_width=True)
    
    st.info("💡 **Analyst Insight:** Notice the strong positive correlation (0.74) between a movie's Budget and Gross Revenue. Interestingly, IMDb Score has almost no correlation (0.18) with Gross Revenue—proving that 'critically acclaimed' movies don't automatically make the most money at the box office!")

# --- TAB 3: HISTORICAL TRENDS ---
with tab_trends:
    st.subheader("Most Profitable Genres Over Time")
    
    # Calculate average profit by genre for the selected year
    genre_profitability = movie_df[movie_df['year'] == selected_year].groupby('genre')['profit'].mean().reset_index()
    genre_profitability = genre_profitability.sort_values(by='profit', ascending=False)

    profit_bar_chart = px.bar(genre_profitability, x='genre', y='profit', color='profit',
                              color_continuous_scale="Viridis",
                              title=f"Average Net Profit by Genre ({selected_year})",
                              labels={"genre": "Movie Genre", "profit": "Net Profit ($)"})
    st.plotly_chart(profit_bar_chart, use_container_width=True)
    
    st.subheader("Are Movies Getting Longer?")
    # Group by year and get average runtime
    historical_runtime = movie_df.groupby('year')['runtime'].mean().reset_index()

    runtime_line_chart = px.line(historical_runtime, x='year', y='runtime', markers=True,
                                 title="Average Movie Runtime (1980 - 2020)",
                                 labels={"year": "Release Year", "runtime": "Average Runtime (Minutes)"})
    st.plotly_chart(runtime_line_chart, use_container_width=True)

# --- 7. DYNAMIC KEY INSIGHT & ATTRIBUTION ---
st.markdown("---")

# The insight dynamically changes based on the calculated ROI!
if avg_roi > 3.0:
    st.success(f"### 💡 The Plot Twist (Key Insight)\n**Highly Profitable!** {selected_genre} movies in {selected_year} saw massive returns, averaging **{avg_roi:.1f}x** their budget. This indicates exceptionally strong audience demand relative to production costs.")
elif 0 < avg_roi < 1.0:
    st.error(f"### 🚨 The Plot Twist (Key Insight)\n**Danger Zone!** On average, {selected_genre} movies in {selected_year} failed to break even (ROI: **{avg_roi:.1f}x**). Production budgets significantly outpaced box office returns.")
elif avg_roi == 0:
    st.warning("### ⚠️ The Plot Twist (Key Insight)\nNot enough financial data available for this specific filter combination to determine profitability.")
else:
    st.info(f"### 💡 The Plot Twist (Key Insight)\n{selected_genre} movies in {selected_year} showed moderate financial performance with an average ROI of **{avg_roi:.1f}x**. Remember, high-budget movies don’t always earn high ratings, so controlling production costs is key to maintaining profitability.")

st.markdown("---")
st.caption("Data Source: Kaggle – Daniel Grijalva, Movie Industry Dataset")