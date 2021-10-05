from flask import Flask, render_template, request, redirect, url_for, session
import random
import questions_db
from questions_db import all_questions, neuro, mechanics_applied, cse, maths_linalg, logic_basic, mathem_logic, krr, hist, hist_greece, phil, phil_presoc, phil_plato_general, phil_aristotle, phil_scholast, hist_islam, phil_arab, words_tr2, words_sp, words_ru, words_ar, words_ja, words_ch, words_ch_hanzi, cse_progr_lang_paradigms, cse_automata_theory, cse_encryption, cse_operating_systems, cse_linux_commands, cse_python, cse_c_plusplus
import jinja2
from jinja2 import Markup
import importlib # for reimporting
import requests # used by google custom image API and by beatiful soup
from bs4 import BeautifulSoup
from flask_session import Session
import high_scores
import high_scores_per_user
import re


app = Flask(__name__, static_folder='static') # references the name of the current module that you're working in (app.py in this case)
app.secret_key = 'siWhw9g438929r^Gguqgd' # secret key is needed for session
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

if __name__ == '__main__':
    app.run(debug=True)


# for gametype = 'random':
number_of_random_questions = 10

#for gametype = 'incr difficulty:'
max_lives = 10 # number of mistakes before game over for the 'increasing_difficulty gametype'
consec_correct_answers_required = 2 # required number of concecutive correctly answered questions, for receiving bonus, for the 'incr difficulty' gametype.
bonuspoints = 2 # bonus points for answering some number of consecutive questions correctly

sound_sample_good = "good1.mp3"
sound_sample_bad = "bad1.mp3"
sound_samples_start = ["start1.mp3", "start2.mp3", "start3.mp3", "start4.mp3","start5.mp3", "start6.mp3", "start7.mp3"]
sound_samples_game_over = ["game_over1.mp3", "game_over2.mp3", "game_over3.mp3","game_over4.mp3", "game_over5.mp3", "game_over6.wav"]


@app.route('/')
def root():
    # check if username is already defined as a key in the user data dictionary:
    try:
        session['username']
    except KeyError: # if username not yet defined, then ask for new login.
        return redirect(f"/login/")
    if session['username'] == None:
        return redirect(f"/login/")
    else:            # otherwise: go to main selection menu
        return redirect(f"/home/")


@app.route('/login/', methods=["GET"])
def login():
    title = "Welcome to this game"
    text = "Before playing the game, please fill in a username: "
    return render_template("login.html", title=title, text=text)


@app.route('/home/', methods=["GET"])
def home():
    try:
        session['username'] = request.args.get("username")
    except KeyError: # if username not yet defined, then ask for new login.
        return redirect(f"/login/")
    if session['username'] == None:
        return redirect(f"/login/")
    else:           # otherwise: continue loading some selection of questions
        session["sound_sample_start"] = random.sample(sound_samples_start, 1)
        return render_template("selection_menu.html", username = session['username'], sound_sample=session["sound_sample_start"], loop=True)


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/selected_category/<category>')
def selected_category(category):
    session['home_ref'] = ('/home/') # url for the home button.
    score = 0 # initial score
    score_rounded = 0 # initial rounded off score
    reward=10 # initial value of 'reward' for gametype 'random'
    reward_rounded=10 # initial value of 'reward' but rounded off.
    mistakes = 0 # initial number of mistakes made, for gametype 'increasing difficulty'
    consec_correct_answers = 0 # initialize this number, used for winning extra points after some number of consecutive correctly answered questions.
    i = 0 # initialize to some index, for selecting a question in the selected_questions list

    # in case username is new, create a new score list in high_scores_per_user.py
    try:
        eval(session["username"])
    except:
        create_user_high_scores(session["username"])


    # Load the highest score obtained by the current user (i.e. username) for the selected category of questions:
    importlib.reload(high_scores_per_user) # reimport the high_scores_per_user.py file


    # initialize the gametype and list of questions (1st argument of split_and_shuffle is: times_shuffled (select 1-5)):
    if category == 'all_questions':
        gametype = 'randomized'
        selected_questions = random.sample(all_questions,number_of_random_questions)
    if category == 'programming_and_os':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(2, cse_progr_lang_paradigms+cse_operating_systems, cse_linux_commands, cse_python+cse_c_plusplus)
    if category == 'theoretical_cs':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(2, cse_automata_theory, cse_encryption)
    if category == 'krr':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(1, krr)
    if category == 'logic':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(2, logic_basic+mathem_logic)
    if category == 'maths_linalg':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(1, maths_linalg)
    if category == 'mechanics':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(1, mechanics_applied)
    if category == 'neuroscience':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(2, neuro)
    if category == 'presoc_and_plato':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, hist_greece, phil_presoc+phil_plato_general)
    if category == 'aristotle_and_scholastics':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, phil_aristotle, phil_scholast)
    if category == 'islamic_world_hist_and_philosophy':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, hist_islam,phil_arab)
    if category == 'words_tr2':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(5, words_tr2)
    if category == 'words_sp':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, words_sp)
    if category == 'words_ru':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, words_ru)
    if category == 'words_ar':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, words_ar)
    if category == 'words_ja':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, words_ja)
    if category == 'words_ch':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(3, words_ch)
    if category == 'words_ch_hanzi':
        gametype = 'increasing_difficulty'
        selected_questions = split_and_shuffle(2, words_ch_hanzi)

    # highlight/mark the dots ('...') in the question with a color for readability:
    for question in selected_questions:
        question[0] = mark_string(question[0], "..")

    # make a copy of all these variables for the user, in his/her session data (dictionary):
    session["category"] = category
    session["gametype"] = gametype
    session["selected_questions"] = selected_questions
    session["score"] = score
    session["score_rounded"] = score_rounded
    session["reward"] = reward
    session["reward_rounded"] = reward_rounded
    session["mistakes"] = mistakes
    session["consec_correct_answers"] = consec_correct_answers
    session["i"] = i
    session["img_urls"] = [] # initializes a list of img urls
    session["indices_of_correctly_answered_questions"] = [] # indices of correctly answered questions, that need removal from the selected_questions, at end of round

    session["hint_button"] = 'on' # initialize setting for button for turning on/off visual hints.
    session["hint_button_set"] = 'on'

    # Load the overall high_score for the selected category of questions:
    session["high_score"] = load_high_score(session["category"])[0] # load high-score
    session["high_score_username"] = load_high_score(session["category"])[1] # load name of user who scored overall high-score

    session["user_high_score"] = load_user_high_score(session["username"], session["category"])

    if session["user_high_score"] < 15:
        return redirect(f"/question/1")
    else:
        return redirect(f"/question/" + str(session["user_high_score"] -14)) # you start with more advanced questions if you previously scored > 15 questions correctly.


@app.route("/question/<question_number>", methods=['GET']) # defines actions for the question screen
def question(question_number):
    question_amount = len(session["selected_questions"])
    hint_button = request.args.get('hint_button_set')
    answer_link = "/answer/" + question_number
    question_link = "/question/" + question_number
    i = int(question_number)
    if hint_button != None:
        session['hint_button'] = hint_button
    session["i"] = i
    session["score_rounded"] = int(session["score"]) if float(session["score"]).is_integer() else float('%.1f'%session["score"])
    if i > len(session["selected_questions"]):
        return redirect(f"/score_report/")
    else:
        answer = str(session["selected_questions"][i-1][1])
        session["img_urls"] = get_images_links(answer)
        if session["gametype"] == 'randomized':
            session["question"] = session["selected_questions"][i-1][0]
            return render_template("question.html", home_ref=session['home_ref'], question=session["question"], hint_button=session['hint_button'], urls=session["img_urls"], i=i, question_amount=question_amount, answer_link=answer_link, score_rounded=session["score_rounded"], high_score=session["high_score"], high_score_username=session["high_score_username"], username = session['username'])
        if session["gametype"] == 'increasing_difficulty':
            lives_left = max_lives-session["mistakes"]
            if lives_left == 0: # for game over, or for winning max score
                return redirect(f"/score_report/")
            else:
                session["question"] = session["selected_questions"][i-1][0]
                return render_template("question_incr.html",home_ref=session['home_ref'], question=session["question"], hint_button=session['hint_button'], urls=session["img_urls"], i=i, question_amount=question_amount, highest_user_score=session["user_high_score"], answer_link=answer_link, score_rounded=question_number, lives_left=lives_left, max_lives=max_lives, high_score=session["high_score"], high_score_username=session["high_score_username"], username = session['username'])


@app.route("/answer/<question_number>", methods=["GET"])
def answer(question_number):
    session["response"] = request.args.get('response')
    i=int(question_number)
    if session["gametype"] == 'randomized':
        next_question = "/question/" + str(int(question_number)+1)
        if session["response"].lower().split() == session["selected_questions"][i-1][1].lower().split(): # if the given response was the correct answer
            session["score"] += session["reward"]
            if session["score"] > session["high_score"]:
                session["score_rounded"] = int(session["score"]) if float(session["score"]).is_integer() else float('%.1f'%session["score"])
                with open('high_scores.py', 'a' ) as fout :    # adjust the high_score in high_scores.py
                    fout.write(str(session["category"]) +' = [' + str(session["score_rounded"]) + ',"' + session['username'] + '"]\n')
                importlib.reload(high_scores) # reimport the high_scores.py file
                session["high_score"] = load_high_score(session["category"])[0]   # update the high_score variable
                session["high_score_username"] = load_high_score(session["category"])[1]
            session["indices_of_correctly_answered_questions"].append(i-1)
            return render_template("answer_correct.html", sound_sample=sound_sample_good, questions=session["selected_questions"], question=session["question"], question_amount=len(session["selected_questions"]), response=session["response"], i=i, reward_rounded=session["reward_rounded"], next_question=next_question, username = session['username'])
        else:
            return render_template("answer_incorrect.html", sound_sample=sound_sample_bad, questions=session["selected_questions"], question=session["question"], question_amount=len(session["selected_questions"]), response=session["response"], i=i, next_question=next_question, username = session['username'])
    if session["gametype"] == 'increasing_difficulty':
        if session["response"].lower().split() == session["selected_questions"][i-1][1].lower().split(): # if the given response was the correct answer
            session["score"] = int(question_number)
            session["consec_correct_answers"] += 1     # counter for how many consecutive questions have been answered correctly
            if session["consec_correct_answers"] < consec_correct_answers_required:
                next_question = "/question/" + str(int(question_number)+1)
            elif session["consec_correct_answers"] == consec_correct_answers_required:
                next_question = "/question/" + str(int(question_number)+bonuspoints)
                session["consec_correct_answers"] = 0 # counter for how many consecutive questions have been answered correctly, reset to 0 after bonuspoints are awarded.
            if int(next_question[10:])-1 > session["high_score"]:
                with open('high_scores.py', 'a' ) as fout :    # adjust the high_score in high_scores.py
                    fout.write(str(session["category"]) +' = [' + str(int(next_question[10:])-1) + ',"' + session['username'] + '"]\n')
                importlib.reload(high_scores) # reimport the high_scores.py file
                importlib.reload(high_scores_per_user) # reimport the high_scores_per_user.py file
                session["high_score"] = load_high_score(session["category"])[0]   # update the high_score variable
                session["high_score_username"] = load_high_score(session["category"])[1]
            if int(next_question[10:])-1 > session["user_high_score"]: # ADJUST THE USER HIGH SCORE TO FILE.
                adjust_user_high_score(session["username"],session["category"],int(next_question[10:])-1)
            return render_template("answer_correct.html",sound_sample=sound_sample_good, questions=session["selected_questions"], question=session["question"], question_amount=len(session["selected_questions"]), response=session["response"], i=i, next_question=next_question, consec_correct_answers=session["consec_correct_answers"], consec_correct_answers_required=consec_correct_answers_required, bonuspoints=bonuspoints, username = session['username'])
        else:
            session["consec_correct_answers"] = 0  # counter for how many consecutive questions have been answered correctly, reset to 0 after false answer
            session["score"] = int(question_number)
            session["mistakes"] += 1
            next_question = "/question/" + str(int(question_number))
            return render_template("answer_incorrect.html", sound_sample=sound_sample_bad, questions=session["selected_questions"], question=session["question"], question_amount=len(session["selected_questions"]), response=session["response"], i=i, next_question=next_question, username = session['username'])

@app.route("/score_report/")
def score_report():
    sound_sample_game_over = random.sample(sound_samples_game_over, 1)
    question_amount  = len(session["selected_questions"])
    delete_multiple_element(session["selected_questions"], session["indices_of_correctly_answered_questions"]) # reduces the set of remaining quesions in gametype: random
    session["indices_of_correctly_answered_questions"] = [] # reset for new round
    session["reward"] = session["reward"]*0.75    # reduces reward points for correct answers; each round the reward decreases. Only used by gametype: random questions
    session["reward_rounded"] = int(session["reward"]) if float(session["reward"]).is_integer() else '%.1f'%session["reward"]
    session["score_rounded"]  = int(session["score"]) if float(session["score"]).is_integer() else float('%.1f'%session["score"])
    if session["gametype"] == 'randomized':
        if len(session["selected_questions"]) == 0:
            score_percentage = '%.1f'%(session["score"])
            return render_template("score_report_final.html", sound_sample=sound_sample_game_over, score_rounded=session["score_rounded"], max_score=100, score_percentage=score_percentage, gametype=session["gametype"], username = session['username'])
        else:
            return render_template("score_report.html", sound_sample=sound_sample_game_over, score_rounded=session["score_rounded"], reward_rounded=session["reward_rounded"])
    if session["gametype"] == 'increasing_difficulty':
        score_percentage = '%.1f'%(session["score"] / len(session["selected_questions"]) * 100)
        return render_template("score_report_final.html", sound_sample=sound_sample_game_over, score_rounded=session["score_rounded"], max_score=len(session["selected_questions"]), score_percentage=score_percentage, gametype=session["gametype"], username = session['username'])

from high_scores_per_user import * # do not place at beginning of file, otherwise it keeps using the original file

def get_images_links(query):
    # first split the multi digit numbers that occur in the query, otherwise the visual hint becomes too informative
    split_query = split_string_wth_numbers(query)
    searchUrl = "https://www.google.com/search?q={}&site=webhp&tbm=isch".format(split_query)
    d = requests.get(searchUrl).text
    soup = BeautifulSoup(d, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls_list = []
    for img in img_tags:
        if img['src'].startswith("http"):
            img_urls_list.append(img['src'])
    random.shuffle(img_urls_list)
    return img_urls_list

def split_string_wth_numbers(some_string):
    # splits multidigit numbers in strings, used in img_url search
    new_string = str(some_string)
    new_string = new_string.replace("-1", "minus one ")
    new_string = new_string.replace("[", "  ")
    new_string = new_string.replace("]", "  ")
    new_string = new_string.replace("0", "zero ")
    new_string = new_string.replace("1", "one ")
    new_string = new_string.replace("2", "two ")
    new_string = new_string.replace("3", "three ")
    new_string = new_string.replace("4", "four ")
    new_string = new_string.replace("5", "five ")
    new_string = new_string.replace("6", "six ")
    new_string = new_string.replace("7", "seven ")
    new_string = new_string.replace("8", "eight ")
    new_string = new_string.replace("9", "nine ")
    return new_string

def delete_multiple_element(list_object, indices): # remove items from a list
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


def split_and_shuffle(times_shuffled, *list_objects): # shuffle the input lists multiple times, according to split_and_shuffle_real
    if times_shuffled in [1,2,3,4,5]:
        a = split_and_shuffle_real(10, *list_objects) # numeric argument = # questions_per_sublist

    if times_shuffled in [2,3,4,5]:
        a = split_and_shuffle_real(7, a)

    if times_shuffled in [3,4,5]:
        a = split_and_shuffle_real(10,a)

    if times_shuffled in [4,5]:
        a = split_and_shuffle_real(7, a)

    if times_shuffled in [5]:
        a = split_and_shuffle_real(10,a)
    return a

def split_and_shuffle_real(questions_per_sublist, *list_objects):
    # first determine k = # of sublists = # of (difficulty levels) to be used
    # make this dependent on the # of questions:
    size_of_question_list = 0
    for list_object in list_objects:
        size_of_question_list += len(list_object)
    k=int(size_of_question_list/questions_per_sublist)
    # splits each list_object into k sublists
    # then assembles 1 sublist for each difficulty level, each containing questions from all list_objects.
    # then it shuffles the questions within each difficulty level.
    # and then finally, it merges all shuffled sublists back into one list
    temp_list = []
    total_list = []
    # create a list of 1 sublist for each list_object,
    # whereby each of these sublists is split into k subsublists:
    for list_object in list_objects:
        new_list = []
        n=len(list_object)//k # size of the sublists
        new_list = [list_object[i:i+n] for i in range(0, len(list_object), n)]
        for index in range(k,len(new_list)):
            for i in range(len(new_list[index])):
                new_list[k-1].append(new_list[index][i])
        for index in range(k,len(new_list)):
            new_list.pop()
        temp_list.append(new_list)
    # combine everything into one list containing k sublists:
    for i in range(k):
        total_list.append(temp_list[0][i])
        for l in range(1,len(list_objects)):
            for item in temp_list[l][i]:
                total_list[i].append(item)
    # shuffle each of these k sublists separately:
    for i in range(k):
        random.shuffle(total_list[i])
    # merge the k sublists back together into 1 big list:
    new_list = [] #reusing new_list
    for i in range(k):
        new_list += total_list[i]
    return new_list

def mark_string(question, some_string):
    # transforms the question into something that replaces 'some_string' in the text.
    # used in this game for marking '..' (dots/blanks) in the question with a color, for improved readability.
    new_question = ''
    split_question = question.split(some_string) # creates a list of strings
    last_item = split_question[-1]
    split_question.pop() # temporarily remove last item, otherwise a marking will be placed also after the last letter of the question.
    for item in split_question:
        item += jinja2.Markup('<mark style="font-weight: bold; color: black; background-color:#ffadd6">...</mark>')
        new_question += item
    new_question += last_item # put last item back in place
    return new_question

def load_high_score(category):   # loads the overall high_scores (incl username) from the high_scores.py file
    if category == 'all_questions':
        high_score = high_scores.all_questions
    elif category == 'programming_and_os':
        high_score = high_scores.programming_and_os
    elif category == 'krr':
        high_score = high_scores.krr
    elif category == 'logic':
        high_score = high_scores.logic
    elif category == 'neuroscience':
        high_score = high_scores.neuroscience
    elif category == 'theoretical_cs':
        high_score = high_scores.theoretical_cs
    elif category == 'maths_linalg':
        high_score = high_scores.maths_linalg
    elif category == 'mechanics':
        high_score = high_scores.mechanics
    elif category == 'presoc_and_plato':
        high_score = high_scores.presoc_and_plato
    elif category == 'aristotle_and_scholastics':
        high_score = high_scores.aristotle_and_scholastics
    elif category == 'islamic_world_hist_and_philosophy':
        high_score = high_scores.islamic_world_hist_and_philosophy
    elif category == 'words_tr2':
        high_score = high_scores.words_tr2
    elif category == 'words_sp':
        high_score = high_scores.words_sp
    elif category == 'words_ru':
        high_score = high_scores.words_ru
    elif category == 'words_ar':
        high_score = high_scores.words_ar
    elif category == 'words_ja':
        high_score = high_scores.words_ja
    elif category == 'words_ch':
        high_score = high_scores.words_ch
    elif category == 'words_ch_hanzi':
        high_score = high_scores.words_ch_hanzi
    return high_score


def create_user_high_scores(username): # creates score table for users who enter a non-existent username
    with open('high_scores_per_user.py', 'a' ) as fout:
        fout.write(username.replace(" ", "_") + ' = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] \n')


def load_user_high_score(username, category): # loads the highest score of the user from the high_scores_per_user.py file
    try:
        user_high_scores = eval(username.replace(" ", "_")) # here it uses that the variables in the high_scores_per_user.py were all imported
    except:
        user_high_score = 0
    else:
        if category == 'all_questions':
            user_high_score = user_high_scores[0]
        elif category == 'programming_and_os':
            user_high_score = user_high_scores[1]
        elif category == 'krr':
            user_high_score = user_high_scores[2]
        elif category == 'logic':
            user_high_score = user_high_scores[3]
        elif category == 'neuroscience':
            user_high_score = user_high_scores[4]
        elif category == 'theoretical_cs':
            user_high_score = user_high_scores[5]
        elif category == 'maths_linalg':
            user_high_score = user_high_scores[6]
        elif category == 'mechanics':
            user_high_score = user_high_scores[7]
        elif category == 'presoc_and_plato':
            user_high_score = user_high_scores[8]
        elif category == 'aristotle_and_scholastics':
            user_high_score = user_high_scores[9]
        elif category == 'islamic_world_hist_and_philosophy':
            user_high_score = user_high_scores[10]
        elif category == 'words_tr2':
            user_high_score = user_high_scores[11]
        elif category == 'words_sp':
            user_high_score = user_high_scores[12]
        elif category == 'words_ru':
            user_high_score = user_high_scores[13]
        elif category == 'words_ar':
            user_high_score = user_high_scores[14]
        elif category == 'words_ja':
            user_high_score = user_high_scores[15]
        elif category == 'words_ch':
            user_high_score = user_high_scores[16]
        elif category == 'words_ch_hanzi':
            user_high_score = user_high_scores[17]
    return user_high_score


def adjust_user_high_score(username, category, new_score):
    try:
        eval(username.replace(" ", "_"))
    except:
        old_scores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        old_scores = eval(username.replace(" ", "_"))
    new_scores = old_scores

    if category == 'all_questions':
        new_scores[0] = new_score
    elif category == 'programming_and_os':
        new_scores[1] = new_score
    elif category == 'krr':
        new_scores[2] = new_score
    elif category == 'logic':
        new_scores[3] = new_score
    elif category == 'neuroscience':
        new_scores[4] = new_score
    elif category == 'theoretical_cs':
        new_scores[5] = new_score
    elif category == 'maths_linalg':
        new_scores[6] = new_score
    elif category == 'mechanics':
        new_scores[7] = new_score
    elif category == 'presoc_and_plato':
        new_scores[8] = new_score
    elif category == 'aristotle_and_scholastics':
        new_scores[9] = new_score
    elif category == 'islamic_world_hist_and_philosophy':
        new_scores[10] = new_score
    elif category == 'words_tr2':
        new_scores[11] = new_score
    elif category == 'words_sp':
        new_scores[12] = new_score
    elif category == 'words_ru':
        new_scores[13] = new_score
    elif category == 'words_ar':
        new_scores[14] = new_score
    elif category == 'words_ja':
        new_scores[15] = new_score
    elif category == 'words_ch':
        new_scores[16] = new_score
    elif category == 'words_ch_hanzi':
        new_scores[17] = new_score

    file = 'high_scores_per_user.py'

    pattern = username.replace(" ", "_") + ' = ' + '[\s\S]*'
    subst = username.replace(" ", "_") + ' = ' + str(new_scores) + '\n'

    # Read contents from file as a single string
    file_handle = open(file, 'r')
    file_string = file_handle.read()
    file_handle.close()

    # RE package allows for replacement (also allowing for (multiline) REGEX)
    file_string = (re.sub(pattern, subst, file_string))

    # Write contents to file.
    # Using mode 'w' truncates the file.
    file_handle = open(file, 'w')
    file_handle.write(file_string)
    file_handle.close()



