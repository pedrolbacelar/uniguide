import streamlit as st
from time import sleep
import json
from matcher import load_student_data, load_universities_database, match
# https://uniguide.streamlit.app/

#------------------------------------------------------- Class & Functions -------------------------------------------------------
class Assistant():
    def __init__(self):
        self.messages = []
        self.role = "assistant"
        self.unimatch_questions = {
            1: "Tell me a little bit more about your hobbies!",
            2: "What fields in the school are you interested in?",
            3: "What is your budget for studying?"
        }
        self.unimatch_on = False
        self.unibuddy_on = False
        self.last_user_reply = ""
        self.user_replies_counter = 0
            

    def print_and_add_message(self, content):
        sleep(time_sleep_fast)
        #--- Print message
        with st.chat_message(self.role):
            st.markdown(content)

        #--- Add to history
        self.messages.append({"role": self.role, "content": content})
        st.session_state.messages.append({"role": self.role, "content": content})
    
    def unimatch_question(self):
        self.print_and_add_message(self.unimatch_questions[self.user_replies_counter])

    def set_unimatch_on(self, value):
        self.unimatch_on = value
    def set_unibuddy_on(self, value):
        self.unibuddy_on = value
    def set_last_user_reply(self, value):
        self.last_user_reply = value
    def update_user_replies_counter(self):
        #--- load the json file
        with open("cache-data.json") as f:
            data = json.load(f)

        #--- update the user_replies_counter
        self.user_replies_counter = data["user_replies_counter"]
        self.user_replies_counter += 1

        #--- update the json file
        data["user_replies_counter"] = self.user_replies_counter
        with open("cache-data.json", "w") as f:
            json.dump(data, f)

    def check_finished_questions(self):
        if self.user_replies_counter > len(self.unimatch_questions):
            self.print_and_add_message("Great! I have all the information I need. Let me find the best university for you! 🎓")
            self.unimatch_on = False
            self.user_replies_counter = 0
            #--- update the json file
            with open("cache-data.json") as f:
                data = json.load(f)
            data["user_replies_counter"] = self.user_replies_counter
            with open("cache-data.json", "w") as f:
                json.dump(data, f)
            return True

    def get_last_user_reply(self):
        return self.last_user_reply

class User():
    def __init__(self):
        self.messages = []
        self.role = "user"

    def print_and_add_message(self, content):
        sleep(time_sleep_fast)
        #--- Print message
        with st.chat_message(self.role):
            st.markdown(content)

        #--- Add to history
        self.messages.append({"role": self.role, "content": content})
        st.session_state.messages.append({"role": self.role, "content": content})

    def update_user_profile(self):
        #--- load the json file
        with open("cache-data.json") as f:
            data = json.load(f)
        data["user_profile"] = data["user_profile"] + self.messages[-1]["content"] + " | "

        #--- update the json file
        with open("cache-data.json", "w") as f:
            json.dump(data, f)

    
    def get_last_reply(self):
        return self.messages[-1]["content"]
    

st.title("UniGuide Chat App")
# ------------------------------------------------------- SETUP -------------------------------------------------------
#--- Initialize Agents
assistant = Assistant()
user = User()

time_sleep_fast = 0.25
time_sleep_longer = 1


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Initial Messages ----
with st.chat_message("assistant"):
    st.markdown("Welcome to the complete experience of UniGuide Chatbot 👋!")
    st.markdown("I am here to help you find the best university for you and also to explore more about the universities information! 📖")
    st.markdown("Please, if you want to find the perfect match for you, type 'UniMatch'. If you want to discover more about the universities, type 'UniBuddy'")

#=======================================================
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
#=======================================================


if prompt := st.chat_input("What is up?"):
    user.print_and_add_message(prompt)

    # ------------------------------------------------------- UniMtach -------------------------------------------------------
    #========================= Introduction ==========================
    if prompt == "UniMatch" or prompt == "unimatch":
        assistant.print_and_add_message("Great! Let's find the perfect match for you! 🎓")
        assistant.print_and_add_message("Please, answer the following questions to help me find the best university for you:")

        #--- Update status unimatch
        assistant.set_unimatch_on(True)
    #================================================================

    #========================= CHECKING ==========================
    if assistant.get_last_user_reply() != user.get_last_reply():
        #--- Update user replies counter
        assistant.update_user_replies_counter()
        assistant.set_last_user_reply(user.get_last_reply())
        assistant.unimatch_on = True

        #--- Update user profile
        user.update_user_profile()
    else:
        assistant.unimatch_on = False
    #--- check if matching is done on the cache
    with open("cache-data.json") as f:
        data = json.load(f)
    if data["matching_done"] == True:
        assistant.unimatch_on = False
        assistant.unibuddy_on = True
    #================================================================
    
    #============================== MATCHING ==============================
    if assistant.check_finished_questions():
        #--- load user profile from json
        student_data = load_student_data()
    
        #--- load universities data from json
        universities_data, universities_names = load_universities_database()

        #--- Match the student data with the universities data
        universities_similarities = match(student_data, universities_data, universities_names)
        # universities_similarities = {uniA: 0. , uniB: 0. , uniC: 0.}
        #--- Sort the universities based on the similarities
        universities_similarities = dict(sorted(universities_similarities.items(), key=lambda item: item[1], reverse=True))

        #------- Printing the Results -------
        sleep(time_sleep_longer)
        assistant.print_and_add_message(f"Based on your answers, I found the best university for you are 🎉")
        
        # Print the 5 best universities and show the similarities
        top_5_universities = list(universities_similarities.items())[:5]
        for uni, sim in top_5_universities:
            assistant.print_and_add_message(f"{uni} with similarity of {int(sim*10000)/100}%")

        # --- Print a bar chart with the similarities and universities
        st.bar_chart(universities_similarities)

        #--- Clean User Profile after match
        with open("cache-data.json") as f:
            data = json.load(f)
        data["user_profile"] = ""
        with open("cache-data.json", "w") as f:
            json.dump(data, f)

        #--- Update the json file with matching done
        with open("cache-data.json") as f:
            data = json.load(f)
        data["matching_done"] = True
        with open("cache-data.json", "w") as f:
            json.dump(data, f)
    #=====================================================================

    #============================== QUESTION ==============================
    if assistant.unimatch_on:
        assistant.unimatch_question()
    #=====================================================================

    
    # ------------------------------------------------------- UniBuddy -------------------------------------------------------
    elif prompt == "UniBuddy":
        assistant.print_and_add_message("Great! Let's explore more about the universities! 📚")
        #--- Update status unibuddy
        assistant.set_unibuddy_on(True)

    if assistant.unibuddy_on:
        st.write("UniBuddy is under construction! 🚧")

        # TODO:
        # - Test API from chatgpt
        # - give an overview of the user profile and the best university, and why it is the best match
        # - ask if the user wants to explore a specific university
        # - use as initial prompt the data from that university and than use chatgpt

