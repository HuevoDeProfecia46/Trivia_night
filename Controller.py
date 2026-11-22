import requests as rq
import os
import pandas as pd
import UI


categories = {'Categories': ["General Knowledge", "Books", "Film","Music", "Musicals and Theatres",
                             "Television", "Video Games", "Board Games", "Science and Nature", "Computer Science",
                             "Math", "Mythology" , "Sports", "Geography" , "History", "Politics", "Art",
                             "Celebrities", "Animal", "Vehicles", "Comics", "Gadgets", "Anime and Manga",
                             "Cartoon and Animation"],
              'index': [9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
              'difficulty': ["easy" , "medium" , "hard"]
              }

base_url = "https://opentdb.com/api.php?"

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

user_data = os.path.join(DATA_FOLDER, "user_data.csv")

def save_to_csv(data_dict):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(user_data):
        df_new.to_csv(user_data, mode='w', header=True, index=False)
    else:
        df_new.to_csv(user_data, mode='a', header=False, index=False)


def load_from_csv():
    if os.path.isfile(user_data):
        return pd.read_csv(user_data)
    else:
        return pd.DataFrame()


def main():
    UI.home_screen(categories)



def category_translator(category , difficulty):
    cat_num = 0
    for num, cat in enumerate(categories['Categories']):
        if cat == category:
            cat_num = categories['index'][num]
    if difficulty == "Easy":
        return cat_num , "easy"
    if difficulty == "Medium":
        return cat_num , "medium"
    else:
        return cat_num , "hard"


def fetch_request(category, difficulty):
    tcat , tdif= category_translator(category, difficulty)
    custom_url = (base_url + "amount=" + str(UI.AMOUNT_OF_QUESTIONS)
                      + "&category=" + str(tcat) + "&difficulty=" + str(tdif))
    response = rq.get(custom_url)
    questions = response.json()
    questions_df = pd.DataFrame(questions)
    questions_df = questions_df.reset_index(drop=True).drop(columns=['response_code'])
    if response.status_code == 200:
        if questions['response_code'] == 0:
            return questions_df
        else:
            return "Error fetching data"
    else:
        return "HTTP error: " + str(response.status_code)



if __name__ == "__main__":
    main()