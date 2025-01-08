import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load SA20 data
@st.cache_data
def load_data():
    return pd.read_csv('Dataset/SA20_data.csv')
    df['total_runs'] = df.apply(lambda x: x['runs_off_bat'] + x['extras'], axis = 1)
    df['isOut'] = df['player_dismissed'].apply(lambda x: 1 if type(x) == type('str') else 0)

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
        df = load_data()
    
        # match_data = data[(data["batting_team"] == chasing_team) & (data["bowling_team"] == bowling_team)]
    
        # Display inputs and options
        st.write(f"Chasing Team: {chasing_team}")
        st.write(f"Bowling Team: {bowling_team}")
        st.write(f"Target: {target}")
    
        t1 = chasing_team
        t2 = bowling_team
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
            i1p_0, i1p_1, i1p_2, i1p_3, i1p_4, i1p_6, i1p_w = get_pbvalues(t1)
            i2p_0, i2p_1, i2p_2, i2p_3, i2p_4, i2p_6, i2p_w = get_pbvalues(t2)
    
            pred_runs = current_score
            pred_wks = current_wickets
            leftover_balls = 300 - current_overs * 6
    
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
    
            return pred_runs
    
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
                        lose_count += 1
    
                win_ls.append(win_count)
                req_runs.append(i)
    
            required_runs = current_score
            for i in range(len(req_runs)):
                if win_ls[i] >= 50:
                    required_runs = req_runs[i]
                    break
    
            return required_runs
    
        def find_wickets(current_score, target, current_wickets, at_overs):
            req_runs = find_runs(current_score, target, current_wickets, at_overs)
    
            win_ls = []
            req_wks = []
            for i in range(current_wickets, 10):
                win_count = 0
                for j in range(100):
                    pred_runs = predict_runs(target, current_score, i, at_overs)
                    result_pred = get_win(pred_runs, target)
    
                    if result_pred == 'win':
                        win_count += 1
    
                win_ls.append(win_count)
                req_wks.append(i)
    
            req_wicket_value = current_wickets
            for i in range(len(req_wks)):
                if win_ls[i] < 45:
                    req_wicket_value = req_wks[i]
                    break
    
            return req_wicket_value
    
        def find_runs_wickets(current_wks, at_overs, target_score):
            plt.figure(figsize=(23, 10))
    
            req_value = find_runs(target_score, current_wks, at_overs)
            req_wk_value = find_wickets(target_score, current_wks, at_overs)
    
            if at_overs == 10:
                req_value = 75
                req_wk_value = 1
    
            y = np.array([req_value for i in range(51)])
    
            plt.scatter(at_overs, req_value, s=3000, color='red')
            plt.axhline(target_score, ls='--', color='blue')
            plt.text(1, target_score + 10, 'Target Score :' + str(target_score), color='darkblue', fontsize=13)
            plt.text(at_overs, req_value, str(req_value) + '/' + str(req_wk_value), color='white', fontsize=12,
                     horizontalalignment='center', verticalalignment='center')
            plt.text(at_overs, req_value - 30, 'IND has to be at ' + str(req_value) + '/' + str(req_wk_value) + ' after ' + str(at_overs) + ' ov', horizontalalignment='center')
            plt.ylim(50, target_score + 50)
            plt.xticks(np.arange(0, 51, 1))
            plt.title('Where should IND be?', fontsize=20)
            plt.xlabel('Overs')
            plt.ylabel('Score')
            st.pyplot(plt)
    
        # Streamlit sliders for user input
        current_wks = st.slider('Current Wickets', min_value=1, max_value=10, step=1, value=1)
        at_overs = st.slider('At Overs', min_value=10, max_value=50, step=1, value=10)
        target_score = st.slider('Target Score', min_value=0, max_value=300, step=1, value=230)
    



if __name__ == "__main__":
    main()

