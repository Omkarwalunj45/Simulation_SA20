import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load SA20 data
@st.cache_data
def load_data():
    return pd.read_csv('Dataset/SA20_data.csv')

# Calculate win probabilities (adapted for T20)
def calculate_win_probability(overs_left, wickets_in_hand, runs_to_target, balls_left):
    """
    Simplified model for T20 win probability calculation.
    """
    base_chance = 0.5  # Base chance for simplicity
    overs_factor = (20 - overs_left) / 20
    wickets_factor = wickets_in_hand / 10
    target_factor = 1 - (runs_to_target / (6 * overs_left + 1))  # Run rate factor

    win_probability = base_chance + 0.3 * overs_factor + 0.4 * wickets_factor + 0.3 * target_factor
    return min(max(win_probability, 0), 1)  # Ensure probability stays between 0 and 1

# Streamlit App
def main():
    st.title("SA20 Chase Simulation")
    st.sidebar.header("Match Setup")

    # Predefined Teams
    teams = [
        "Paarl Royals",
        "MI Cape Town",
        "Joburg Super Kings",
        "Durban's Super Giants",
        "Pretoria Capitals",
        "Sunrisers Eastern Cape"
    ]

    # User inputs
    chasing_team = st.sidebar.selectbox("Select Chasing Team:", teams)
    bowling_team = st.sidebar.selectbox("Select Bowling Team:", [team for team in teams if team != chasing_team])
    target = st.sidebar.number_input("Enter Target Runs:", min_value=1, step=1)

    # Load and filter data
    data = load_data()

    match_data = data[(data["batting_team"] == chasing_team) & (data["bowling_team"] == bowling_team)]

    # Display inputs and options
    st.write(f"Chasing Team: {chasing_team}")
    st.write(f"Bowling Team: {bowling_team}")
    st.write(f"Target: {target}")

    # Simulation: Calculate probabilities
    overs_left = st.sidebar.slider("Overs Left:", min_value=1, max_value=20, value=20)
    wickets_in_hand = st.sidebar.slider("Wickets In Hand:", min_value=1, max_value=10, value=10)

    # Validate `target` for the slider
    if target < 1:
        target = 1

    runs_to_target = st.sidebar.slider(
        "Runs Needed to Target:", min_value=1, max_value=int(target), value=int(target)
    )

    balls_left = overs_left * 6

    win_prob = calculate_win_probability(overs_left, wickets_in_hand, runs_to_target, balls_left)

    # Display Probability
    st.write(f"Win Probability: {win_prob * 100:.2f}%")

    # Visualization
    fig, ax = plt.subplots()
    ax.bar(["Win", "Lose"], [win_prob * 100, (1 - win_prob) * 100], color=["green", "red"])
    ax.set_ylabel("Probability (%)")
    ax.set_title("Win vs Lose Probability")
    st.pyplot(fig)



if __name__ == "__main__":
    main()

