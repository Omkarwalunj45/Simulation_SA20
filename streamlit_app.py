import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load SA20 data
@st.cache_data
def load_data():
    data = pd.read_csv("Dataset/SA20_data.csv")
    return data

# Function to calculate win probability
def calculate_win_probability(overs_left, wickets_in_hand, runs_left):
    # Adjusted formula for T20 win probability calculation
    max_overs = 20
    win_prob = (1 - (runs_left / (overs_left * 6))**2) * (wickets_in_hand / 10)
    return max(0, min(win_prob, 1))  # Clamp between 0 and 1

# Streamlit app
def main():
    st.title("SA20 Interactive Simulation Model")

    # Step 1: User Inputs
    st.sidebar.header("Match Setup")
    team1 = st.sidebar.text_input("Enter Team 1 (Bowling Team):", "Team A")
    team2 = st.sidebar.text_input("Enter Team 2 (Chasing Team):", "Team B")
    target = st.sidebar.number_input("Enter Target for Chasing Team:", min_value=0, value=150)
    current_runs = st.sidebar.number_input("Current Runs Scored by Chasing Team:", min_value=0, value=0)
    current_overs = st.sidebar.number_input("Overs Completed by Chasing Team:", min_value=0.0, max_value=20.0, value=0.0)
    wickets_lost = st.sidebar.number_input("Wickets Lost by Chasing Team:", min_value=0, max_value=10, value=0)

    # Step 2: Data Preprocessing
    data = load_data()
    chasing_team_data = data[(data['batting_team'] == team2) & (data['bowling_team'] == team1)]

    st.write(f"Chasing Team: {team2} vs Bowling Team: {team1}")
    st.write(f"Target: {target}, Current Runs: {current_runs}, Current Overs: {current_overs}, Wickets Lost: {wickets_lost}")

    # Step 3: Calculate Remaining Values
    overs_left = 20 - current_overs
    wickets_in_hand = 10 - wickets_lost
    runs_left = target - current_runs

    # Step 4: Win Probability
    win_prob = calculate_win_probability(overs_left, wickets_in_hand, runs_left)

    st.metric("Win Probability (%)", round(win_prob * 100, 2))

    # Step 5: Simulation (Ball-by-Ball Updates)
    st.subheader("Ball-by-Ball Simulation")
    num_balls = int(overs_left * 6)
    simulation_data = []

    for ball in range(1, num_balls + 1):
        runs_this_ball = np.random.choice([0, 1, 2, 3, 4, 6], p=[0.4, 0.3, 0.15, 0.05, 0.07, 0.03])
        runs_left -= runs_this_ball
        win_prob = calculate_win_probability(overs_left, wickets_in_hand, runs_left)
        simulation_data.append([ball, runs_this_ball, max(runs_left, 0), round(win_prob * 100, 2)])
        overs_left = max(0, overs_left - (1 / 6))

    sim_df = pd.DataFrame(simulation_data, columns=["Ball", "Runs This Ball", "Runs Left", "Win Probability (%)"])
    st.dataframe(sim_df)

    # Step 6: Visualization
    st.subheader("Win Probability Chart")
    plt.figure(figsize=(10, 6))
    plt.plot(sim_df["Ball"], sim_df["Win Probability (%)"], marker="o", color="blue")
    plt.title("Win Probability Over Balls")
    plt.xlabel("Ball")
    plt.ylabel("Win Probability (%)")
    st.pyplot(plt)

if __name__ == "__main__":
    main()
