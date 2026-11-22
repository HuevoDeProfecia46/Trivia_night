import streamlit as st
import pandas as pd
import random
from Controller import fetch_request, save_to_csv, load_from_csv

st.set_page_config(
    page_title="Trivia Night",
    page_icon="🧠",
    layout="centered"
)

if "number_of_questions" not in st.session_state:
    st.session_state["number_of_questions"] = 15
if "consent" not in st.session_state:
    st.session_state["consent"] = True

AMOUNT_OF_QUESTIONS = st.session_state["number_of_questions"]
CONSENT = st.session_state["consent"]



def home_screen(categories):
    if "screen" not in st.session_state:
        st.session_state["screen"] = "home"
    if st.session_state["screen"] == "home":
        st.title("Trivia Night", text_alignment="center")
        st.caption("Test your knowledge throughout 24 categories and find out how you compare to other players!")
        with st.container(border=True):
            col1, col2 , col3 = st.columns(3)
            with col2:
                st.write()
                if st.button("Play" , width=175 , type="primary" , icon=":material/sports_esports:"):
                    st.session_state["screen"] = "pregame"
                    st.rerun()
                if st.button("Player statistics" , width=175 , type="secondary" , icon=":material/analytics:"):
                    st.session_state["screen"] = "stats"
                    st.rerun()
                if st.button("Options" , width=175 , type="secondary", icon=":material/settings:"):
                    options()
        st.subheader("About Trivia Night", text_alignment="center")
        st.write("Trivia Night is a class project for Human Computer Interaction created by Angel Santana. It uses "
                 "the Open Trivia Database API to fetch questions and display them as a fun quiz! Open Trivia Database "
                 "is fully community driven, so you can add questions of your own and have them appear on this quiz. "
                 "Now show us what you got and play some trivia!")
    if st.session_state["screen"] == "pregame":
        pre_game(categories)
    if st.session_state["screen"] == "stats":
        view_stats()
    if st.session_state["screen"] == "trivia":
        trivia()
    if st.session_state["screen"] == "game_over":
        game_over()


def view_stats():
    st.title("Trivia Night", text_alignment="center")
    st.subheader("Global Statistics")
    st.divider()
    global_data = load_from_csv().copy()
    global_data["answers"]  = translate_df(global_data["answers"])
    if global_data.empty:
        st.warning("No data available to show, change that by playing!")
    else:
        st.dataframe(global_data,width=1000, height="content")
    if st.button("← Return to home screen"):
        st.session_state["screen"] = "home"
        st.rerun()



@st.dialog("Settings")
def options():
    global AMOUNT_OF_QUESTIONS, CONSENT
    num = st.slider("Select number of questions", min_value=1, max_value=50, value=15, step=1)
    st.session_state["number_of_questions"] = num
    AMOUNT_OF_QUESTIONS = st.session_state["number_of_questions"]
    st.write("This website collects data on the inputs of each question for data analysis purposes. We do not "
             "share this data with anybody else. Would you like to turn off data collection?")
    if st.checkbox("Turn off data collection"):
        update_consent = False
    else:
        update_consent = True
    st.session_state["consent"] = update_consent
    CONSENT = st.session_state["consent"]
    st.caption("Note: this means you will not be able to compare your answers to other users.")





def pre_game(categories):
    st.title("Trivia Night", text_alignment="center")
    st.caption("Select your category and difficulty" , text_alignment="center")
    if "category" not in st.session_state:
        st.session_state["category"] = categories['Categories'][0]
    if "difficulty" not in st.session_state:
        st.session_state["difficulty"] = categories['difficulty'][1]
    with st.container(border=True):

        st.subheader("Select Category")
        st.session_state["category"] = st.selectbox(
            "Select your preferred category", categories['Categories'])

        st.subheader("Select Difficulty")

        st.session_state["difficulty"] = difficulty = st.radio(
            "What sort of challenge are you looking for?",
            ["Easy", "Medium", "Hard"],
            horizontal=True
        )


        # Difficulty descriptions
        if difficulty == "Easy":
            st.info("🟢 Easy: Perfect for beginners!")
        elif difficulty == "Medium":
            st.warning("🟡 Medium: A balanced challenge.")
        else:
            st.error("🔴 Hard: Only for trivia experts!")

    col1, col2, col3 = st.columns([5, 4 , 3.7] , gap="large")
    with col1:
        if st.button("← Return to home screen"):
            st.session_state["screen"] = "home"
            st.rerun()
    with col3:
        if st.button("Start Trivia Night!"):
            category = st.session_state["category"]
            difficulty = st.session_state["difficulty"]
            if "questions" not in st.session_state:
                st.session_state["questions"] = fetch_request(category, difficulty)
            st.session_state["screen"] = "trivia"
            st.rerun()

def trivia():
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {"number_of_questions": AMOUNT_OF_QUESTIONS ,"answers": [-1] * AMOUNT_OF_QUESTIONS}
    user_answers = st.session_state["user_answers"]
    if "question_count" not in st.session_state:
        st.session_state["question_count"] = 0
    num = st.session_state["question_count"]
    st.title("Trivia Night!!!", text_alignment="center")
    st.subheader(st.session_state["category"], text_alignment="center")
    with st.container(border=True):
        if num >= AMOUNT_OF_QUESTIONS:
            st.session_state["screen"] = "game_over"
            st.rerun()
        else :
            st.session_state["question_count"] += 1
        button_logic(user_answers, num)
        if st.button("← Return to home screen"):
            st.session_state["screen"] = "home"
            st.rerun()

    answer_message(user_answers, num)


def game_over():
    st.title("Trivia Night", text_alignment="center")
    st.subheader("Results", text_alignment="center")
    st.divider()
    st.write("Well done! Here is the summary of your performance on the quiz:")
    with st.container(border=True, width="stretch"):
        col1, col2, col3 = st.columns([2.5, 2.5, 1])
        with col1:
            st.metric("Number of Questions", AMOUNT_OF_QUESTIONS)
        with col2:
            user_average = take_average()
            st.metric("Accuracy" , (str(user_average) + "%"))
        with col3:
            st.metric("Best Streak" , best_streak())
    if CONSENT:
        data_df = load_from_csv()
        if data_df.empty:
            st.error("There is no other player data, refer your friends!")
        else:
            st.write("This is how other players answered each question:")
            total_answers ,total_average = compare_metrics(data_df)
            if total_average == -1:
                st.error("There is currently no data available for the amount  of questions you attempted")
            else:
                graph_average = st.session_state["user_answers"]["answers"].copy()
                for num, val in enumerate(graph_average):
                    if val == 0:
                        graph_average[num] = 100
                    else:
                        graph_average[num] = 0
                line_df = pd.DataFrame({"Other user's answers": total_average , "your answers": graph_average})
                st.line_chart(line_df, x_label="Question number", y_label="Answer")
                with st.container(border=True, width="stretch"):
                    st.subheader("You average vs other's average:")
                    col1, col2, col3 = st.columns([1.5, 5, 1])
                    col4, col5, col6 = st.columns([1.5, 5, 1])
                    with col1:
                        st.write("Your score")
                    with col3:
                        st.write(str(user_average) + "%")
                    with col2:
                        st.progress(user_average/100, width=400)
                    with col4:
                        st.write("Other user's scores")
                    with col6:
                        others_average = 100 - combined_averages(total_answers)
                        st.write(str(others_average) + "%")
                    with col5:
                        st.progress(others_average / 100, width=400)
    if st.button("← Return to home screen"):
        if "question_count" in st.session_state:
            del st.session_state["question_count"]
        if "user_answers" in st.session_state:
            if CONSENT:
                save_to_csv(st.session_state["user_answers"])
            del st.session_state["user_answers"]
        if "questions" in st.session_state:
            del st.session_state["questions"]
        if "number_of_questions" in st.session_state:
            del st.session_state["number_of_questions"]
        if "consent" in st.session_state:
            del st.session_state["consent"]
        st.session_state["screen"] = "home"
        st.rerun()



def randomize_answer_order(answers):
    ordered_answers = list(answers)
    random.shuffle(ordered_answers)
    return ordered_answers


def replace_value(user_answers, index , value):
    user_answers[index] = value



def button_logic(user_answers, num):
    questions = st.session_state["questions"]
    col1, col2, col3 = st.columns([5, 0.1, 0.1])
    with col1:
        st.subheader("Question " + str(num+1), text_alignment="center")
        st.write(questions["results"][num]["question"])
        with st.container(border=True):
            if questions["results"][num]["type"] == "boolean":
                col1, col2, col3 = st.columns([0.5, 0.5, 0.5])
                with col1:
                    st.button("True", on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == "True"
                    else replace_value(user_answers["answers"], num, 1))
                with col3:
                    st.button("False", on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == "False" else replace_value(
                        user_answers["answers"], num, 1))
            elif questions["results"][num]["type"] == "multiple":
                col1, col2 = st.columns([0.5, 0.5])
                answers = questions["results"][num]["incorrect_answers"] + [questions["results"][num]["correct_answer"]]
                randomize_answer_order(answers)
                with col1:
                    st.button(answers[0], width=300, on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == answers[0]
                    else replace_value(user_answers["answers"], num, 1))
                    st.button(answers[1], width=300, on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == answers[1]
                    else replace_value(user_answers["answers"], num, 1))
                with col2:
                    st.button(answers[2], width=300, on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == answers[2]
                    else replace_value(user_answers["answers"], num, 1))
                    st.button(answers[3], width=300, on_click=lambda: replace_value(user_answers["answers"], num, 0)
                    if questions["results"][num]["correct_answer"] == answers[3]
                    else replace_value(user_answers["answers"], num, 1))

@st.fragment
def answer_message(user_answers , num):
    message = st.empty()
    if user_answers["answers"][num-1] == 1:
        message.error(":material/cancel:Incorrect answer :(")
    elif user_answers["answers"][num-1] == 0:
        message.success(":material/check_circle: Well done, that is the correct answer :)")


def take_average():
    answers = st.session_state["user_answers"]["answers"]
    print(answers)
    correct_answers = 0
    for ans in answers:
        if ans == 0:
            correct_answers += 1

    return round((correct_answers / len(answers)) * 100, 1)


def best_streak():
    answers = st.session_state["user_answers"]["answers"]
    longest_streak = 0
    current_streak = 0
    for ans in answers:
        if ans == 0:
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
    return longest_streak

def compare_metrics(df):
    data_df = df.loc[df["number_of_questions"] == AMOUNT_OF_QUESTIONS].copy()
    if data_df.empty:
        return -1, -1
    answers = parse_answers(data_df["answers"])
    correctness_percentage = [0]*AMOUNT_OF_QUESTIONS
    for arr in answers["answers"]:
        for ind, ans in enumerate(arr):
            correctness_percentage[ind] += arr[ind]

    for ind,val in enumerate(correctness_percentage):
        correctness_percentage[ind] /= len(answers["answers"])
        correctness_percentage[ind]*=100
        correctness_percentage[ind] = 100 - correctness_percentage[ind]

    return answers , correctness_percentage


def parse_answers(answers):
    my_list = []
    for arr in answers:
        rows = []
        for string in arr:
            if string == "[" or string == "]" or string == "," or string == " ":
                continue
            else:
                rows.append(int(string))
        my_list.append(rows)
    return pd.DataFrame({"answers": my_list})


def combined_averages(total_answers):
    average_list = [0]*AMOUNT_OF_QUESTIONS
    average = 0
    for arr in total_answers["answers"]:
        for ind, ans in enumerate(arr):
            average_list[ind] += arr[ind]

    for ind,val in enumerate(average_list):
        average_list[ind] /= len(average_list)
        average_list[ind]*=100
        average+=average_list[ind]

    return round(average/len(total_answers["answers"]), 1)

def translate_df(df):
    my_df = parse_answers(df)
    for arr in my_df["answers"]:
        for ind, ans in enumerate(arr):
            if arr[ind] == 0:
               arr[ind] = "✅"
            else:
                arr[ind] = "❌"
    return my_df