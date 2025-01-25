import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Load ODI data
@st.cache_data
def load_data():
    return pd.read_csv('Dataset/odi_latest.csv')

# Calculate win probabilities (adapted for T20)

# Streamlit App
def main():
        st.title("ODI Cricket Chase Simulation")
        st.sidebar.header("Match Setup")
    
        # Predefined Teams
        teams = ['Australia', 'Pakistan', 'New Zealand', 'India',
               'Bangladesh', 'South Africa', 'England', 'Sri Lanka',
               'West Indies','Afghanistan']
        # User inputs
        chasing_team = st.sidebar.selectbox("Select Chasing Team:", teams)
        bowling_team = st.sidebar.selectbox("Select Bowling Team:", [team for team in teams if team != chasing_team])
        current_score = st.sidebar.number_input("Enter Current Runs:", min_value=0, step=1)
        current_wks = st.sidebar.number_input("Enter Current Wickets:", min_value=0, step=1)
        current_overs = st.sidebar.number_input("Enter Current Overs:", min_value=0, step=1)
        target = st.sidebar.number_input("Enter Target Runs:", min_value=1, step=1)
        current_runs=current_score
        # Load and filter data
        df = load_data()
        # df['total_runs'] = df.apply(lambda x: x['runs_off_bat'] + x['extras'], axis = 1)
        df=df.rename(columns={'is_wkt':'isOut'})
        
    
        # match_data = data[(data["batting_team"] == chasing_team) & (data["bowling_team"] == bowling_team)]
    
        # Display inputs and options
        st.write(f"Chasing Team: {chasing_team}")
        st.write(f"Bowling Team: {bowling_team}")
        # st.write(f"Target: {target}")
    
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
            if teamName == t1:
                p_0 = t1_pb[0]
                p_1 = t1_pb[0] + t1_pb[1]
                p_2 = t1_pb[0] + t1_pb[1] + t1_pb[2]
                p_3 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3]
                p_4 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3] + t1_pb[4]
                p_6 = t1_pb[0] + t1_pb[1] + t1_pb[2] + t1_pb[3] + t1_pb[4] + t1_pb[5]
                p_w = 0.8
            elif teamName == t2:
                p_0 = t2_pb[0]
                p_1 = t2_pb[0] + t2_pb[1]
                p_2 = t2_pb[0] + t2_pb[1] + t2_pb[2]
                p_3 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3]
                p_4 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3] + t2_pb[4]
                p_6 = t2_pb[0] + t2_pb[1] + t2_pb[2] + t2_pb[3] + t2_pb[4] + t2_pb[5]
                p_w = 0.8
            return p_0, p_1, p_2, p_3, p_4, p_6, p_w
    
        def predict_runs(target, current_score, current_wickets, current_overs):
            i1p_0, i1p_1, i1p_2, i1p_3, i1p_4, i1p_6, i1p_w = get_pbvalues(t2)
            i2p_0, i2p_1, i2p_2, i2p_3, i2p_4, i2p_6, i2p_w = get_pbvalues(t1)
    
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
        #WIN wrt Chasing Team
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
                if (win_ls[i] >= 50):
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
                if win_ls[i] <= 40:
                    req_wicket_value = req_wks[i]
                    break
    
            return req_wicket_value

        current_wks = st.slider("Current Wickets", min_value=0, max_value=9, step=1, value=1)
        at_overs = st.slider("At Overs", min_value=10, max_value=50, step=1, value=current_overs)
        target_score = st.slider("Target Score", min_value=0, max_value=450, step=10, value=target)
        
        # Find required runs and wickets
        req_value = find_runs(current_score,target_score, current_wks, at_overs)
        req_wk_value = find_wickets(current_score,target_score, current_wks, at_overs)
        
        if at_overs == current_overs:
            req_value = current_score
            req_wk_value = current_wks
        
        # Plotting
        fig, ax = plt.subplots(figsize=(70, 45))
        y = np.array([req_value for _ in range(51)])
        x = np.arange(1, 51)
        
        ax.scatter(at_overs, req_value, s=500, color='red', label="Required Position")
        ax.axhline(target_score, ls='--', color='blue', label="Target Score")
        ax.text(1, target_score, f"Target Score: {target_score}", color='darkblue', fontsize=42)
        ax.text(at_overs, req_value, f"{req_value}/{req_wk_value}", color='white', fontsize=62, 
                horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='red', alpha=0.5))
        ax.text(at_overs, req_value, f"{t1} has to be at {req_value}/{req_wk_value} after {at_overs} overs", 
                horizontalalignment='center', fontsize=48)
        ax.set_ylim(0, target_score)
        ax.set_xticks(np.arange(10, 51, 5))
        ax.set_title(f"Where should {t1} be?", fontsize=44)
        ax.set_xlabel("Overs")
        ax.set_ylabel("Score")
        ax.legend()
        
        # Displaying the plot
        st.pyplot(fig)
        
        # Display current score
        st.write(f"**Current Score for {t1}:** {current_runs}/{current_wks} ({current_overs} overs)")




if __name__ == "__main__":
    main()

