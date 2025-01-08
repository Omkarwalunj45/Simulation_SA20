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
    t1= chasing_team
    t1_outs = df[df.batting_team == t1].isOut.sum()
    t2_outs = df[df.batting_team == t2].isOut.sum()
    t1_outcomes = df[df.batting_team == t1].total_runs.value_counts()
    t2_outcomes = df[df.batting_team == t2].total_runs.value_counts()
    outcomes = [0, 1, 2, 3, 4, 6, 'w']
    t1_outcomes_count = []
    for outcome in outcomes:
        try:
            if outcome != 'w':
                t1_outcomes_count.append(t1_outcomes[outcome])
            else:
                t1_outcomes_count.append(t1_outs)
        except:
            t1_outcomes_count.append(0)
    
    
    t2_outcomes_count = []
    for outcome in outcomes:
        try:
            if outcome != 'w':
                t2_outcomes_count.append(t2_outcomes[outcome])
            else:
                t2_outcomes_count.append(t2_outs)
        except:
            t2_outcomes_count.append(0)

    t1_pb = [i/sum(t1_outcomes_count) for i in t1_outcomes_count]
    t2_pb = [i/sum(t2_outcomes_count) for i in t2_outcomes_count]    

    def get_pbvalues(teamName):
    if teamName == 't1':
        p_0 = t1_pb[0]
        p_1 = t1_pb[0] + t1_pb[1]
        p_2 = t1_pb[0] + t1_pb[1] + t1_pb[2]
        p_3 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3]
        p_4 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3] + t1_pb[4]
        p_6 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3] + t1_pb[4] + t1_pb[5]
        p_w = 1

    elif teamName == 't2':
        p_0 = t2_pb[0]
        p_1 = t2_pb[0] + t2_pb[1]
        p_2 = t2_pb[0] + t2_pb[1] + t2_pb[2]
        p_3 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3]
        p_4 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3] + t2_pb[4]
        p_6 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3] + t2_pb[4] + t2_pb[5]
        p_w = 1

    return p_0, p_1, p_2, p_3, p_4, p_6, p_w

    def predict_runs(target, current_score, current_wickets, current_overs):

    # pb values of both teams
    i1p_0, i1p_1, i1p_2, i1p_3, i1p_4, i1p_6, i1p_w = get_pbvalues(t1)
    i2p_0, i2p_1, i2p_2, i2p_3, i2p_4, i2p_6, i2p_w = get_pbvalues(t2)

    pred_runs = current_score
    pred_wks = current_wickets
    leftover_balls = 300 - current_overs*6

    for i in range(leftover_balls):
        r_value = np.random.random()

        if r_value <= i2p_0:
            pred_runs += 0
        elif r_value <= i2p_1:
            pred_runs += 1
        elif r_value <= i2p_2:
            pred_runs += 2
        elif r_value <= i2p_3:
            pred_runs += 3
        elif r_value <= i2p_4:
            pred_runs += 4
        elif r_value <= i2p_6:
            pred_runs += 6
        else:
            pred_runs += 0
            pred_wks += 1
            if pred_wks == 10:
                break
        if pred_runs > target:
            break
        # print('pred_runs: ', pred_runs)
        # print('pred_wks: ', pred_wks)

        return pred_runs
    def find_wickets(current_score, target, current_wickets, at_overs):

    #     find_runs(current_score, target, current_wickets, at_overs)
        req_runs = find_runs(current_score, target, current_wickets, at_overs)
    
        runs_ls = []
        results_ls = []
    
        req_wks = []
        win_ls = []
    
        for i in range(current_wickets, 10):
            win_count = 0
            tie_count = 0
            lose_count = 0
    
            for j in range(100):
    #             pred_runs = predict_runs(target, req_runs, i, at_overs)
                pred_runs = predict_runs(target, current_score, i, at_overs)
                runs_ls.append(pred_runs)
                result_pred = get_win(pred_runs, target)
                results_ls.append(result_pred)
    
                if result_pred == 'win':
                    win_count += 1
                elif result_pred == 'tie':
                    tie_count += 1
                else:
                    lose_count +=1
    
            win_ls.append(win_count)
            req_wks.append(i)
    #         print('wickets: ', i, ' win%: ', win_count)
    
        req_wicket_value = current_wickets
    
        for i in range(len(req_wks)):
            if (win_ls[i] < 45)  :
                req_wicket_value = req_wks[i]
                break
    
        return req_wicket_value
    
    def get_win(pred_runs, target):
    if pred_runs > target:
        return 'win'
    elif pred_runs == target:
        return 'tie'
    else:
        return 'lose'



    def find_runs(current_score, target, current_wickets, at_overs):
        runs_ls = []
        results_ls = []
    
        req_runs = []
        win_ls = []
    
        for i in range(current_score, target + 1):
            win_count = 0
            tie_count = 0
            lose_count = 0
    
            for j in range(100):
                pred_runs = predict_runs(target, i, current_wickets, at_overs)
                runs_ls.append(pred_runs)
                result_pred = get_win(pred_runs, target)
                results_ls.append(result_pred)
    
                if result_pred == 'win':
                    win_count += 1
                elif result_pred == 'tie':
                    tie_count += 1
                else:
                    lose_count +=1
    
                win_ls.append(win_count)
                req_runs.append(i)
                # print('runs: ', i, ' win%: ', win_count)
    
        required_runs = current_score
        for i in range(len(req_runs)):
            if win_ls[i] >= 50:
                required_runs = req_runs[i]
                # print('Runs to be: ', req_runs[i])
                break
    
        return required_runs

    # # Display Probability
    # st.write(f"Win Probability: {win_prob * 100:.2f}%")

    # Visualization
    fig, ax = plt.subplots()
    ax.bar(["Win", "Lose"], [win_prob * 100, (1 - win_prob) * 100], color=["green", "red"])
    ax.set_ylabel("Probability (%)")
    ax.set_title("Win vs Lose Probability")
    st.pyplot(fig)



if __name__ == "__main__":
    main()

