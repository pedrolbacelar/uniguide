import streamlit as st
from time import sleep
import json

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
    if prompt == "UniMatch" or prompt == "unimatch":
        assistant.print_and_add_message("Great! Let's find the perfect match for you! 🎓")
        assistant.print_and_add_message("Please, answer the following questions to help me find the best university for you:")

        #--- Update status unimatch
        assistant.set_unimatch_on(True)


    if assistant.get_last_user_reply() != user.get_last_reply():
        #--- Update user replies counter
        assistant.update_user_replies_counter()
        assistant.set_last_user_reply(user.get_last_reply())
        assistant.unimatch_on = True

        #--- Update user profile
        user.update_user_profile()
    else:
        assistant.unimatch_on = False

    
    # ---- Check to see if there is a new answer from the user ----
    #st.write(f"Assistant unimatch_on: {assistant.unimatch_on}")
    #st.write(f"(assitant)last_user_reply: {assistant.get_last_user_reply()}")
    #st.write(f"(user)user_last_reply: {user.get_last_reply()}")
    #st.write(f"User replies counter: {assistant.user_replies_counter}")
    
    
    #--- Case of finished questions
    if assistant.check_finished_questions():
        #--- load user profile from json
        with open("cache-data.json") as f:
            data = json.load(f)
        user_profile = data["user_profile"]
        st.write(f"User Profile: {user_profile}")
        
        #--- Clean User Profile after match
        pass


    # ---- Question Loop for UniMatch ----
    if assistant.unimatch_on:
        assistant.unimatch_question()

    


    # ------------------------------------------------------- UniBuddy -------------------------------------------------------
    elif prompt == "UniBuddy":
        assistant.print_and_add_message("Great! Let's explore more about the universities! 📚")

        #--- Update status unibuddy
        assistant.set_unibuddy_on(True)
        pass

