import streamlit as st
import pandas as pd
import plotly.express as px

# Load the cleaned dataset
df = pd.read_csv("movies.csv")

# Drop rows with missing values in critical columns
df = df.dropna(subset=["year", "genre", "score", "budget", "gross", "votes"])

# Title of the dashboard
st.title("Team Plot Twist Dashboard")

# Filters
year = st.slider("Select Year", int(df['year'].min()), int(df['year'].max()), 2010)
genre = st.selectbox("Select Genre", df['genre'].unique())

# Apply filters
filtered = df[(df['year'] == year) & (df['genre'] == genre)]

# Chart 1: Movies Released Per Year (filtered by genre)
year_count = df[df['genre'] == genre].groupby("year")["name"].count().reset_index()
fig1 = px.line(year_count, x="year", y="name",
               title=f"Movies Released Per Year ({genre})")
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Average IMDb Score by Genre (filtered by year)
genre_score = df[df['year'] == year].groupby("genre")["score"].mean().reset_index()
fig2 = px.bar(genre_score, x="genre", y="score",
              title=f"Average IMDb Score in {year}", color="genre")
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Budget vs Gross (filtered by year + genre)
fig3 = px.scatter(filtered, x="budget", y="gross", size="votes", color="genre",
                  hover_data=["name","year"],
                  title=f"Budget vs Gross Revenue ({genre}, {year})")
st.plotly_chart(fig3, use_container_width=True)

# Key Insight
st.markdown("### 📌 Key Insight: High-budget movies don’t always earn high ratings")

# Attribution
st.markdown("---")
st.caption("Data Source: Kaggle – Daniel Grijalva, Movie Industry Dataset")
st.caption("Team Members: Reynalen Leigh Alenzuela, Gabriel Barabad, Kirk Johnray Menez")
