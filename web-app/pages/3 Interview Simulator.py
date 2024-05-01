import streamlit as st
from modules import core_prompts as cp
from modules import gif_generator as gg
from modules import formatter as fmt

# Set page title
st.set_page_config(page_title="Interview Simulator by ANUKS")

# Initialise session_state
if 'int_sim_state' not in st.session_state:
    # State of the webpage
    # 1. initialize - initial condition of the webpage
    # 2. choose_role - choose whether to be interviewer or applicant
    # 3. applicant - chat as an applicant
    # 4. interviewer - chat as an interviewer
    st.session_state['int_sim_state'] = "initialize"

match st.session_state['int_sim_state']:
     
    case "initialize":
        # The initial form of the webpage
        if "form_filled" not in st.session_state:
            st.markdown("## Interview Simulator")
            st.warning('Please input and submit the form in the home page.', icon="⚠️")
            if st.button("Go back to home"):
                st.switch_page('0 Home.py')
        else:
            # Reload webpage with ready state
            st.session_state['int_sim_state'] = "choose_role"
            st.rerun()

    case "choose_role":
        # Initialize and clear chat history
        st.session_state.sim_messages = []
        st.session_state['int_sim_toggle_comment'] = False 
        # Ask user to choose the role
        st.markdown("## Interview Simulator")
        st.markdown("Roleplay either as an applicant or interviewer.")
        st.markdown("- Applicant: respond to the interviewer, either by yourself or with the AI help.")
        st.markdown("- Interviewer: inverse the typical roleplay, and save time write answers to funny interview questions.")
        st.markdown("#### Please choose which role you want to play:")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Applicant", use_container_width=True):
                st.session_state['int_sim_state'] = "applicant"
                st.rerun()
        with col2:
            if st.button("Interviewer", use_container_width=True):
                st.session_state['int_sim_state'] = "interviewer"
                st.rerun()

    case "applicant":
        # Display chat messages 
        for message in st.session_state.sim_messages:
            if message['role'] == "tacit_commenter":
                if st.session_state['int_sim_toggle_comment'] == False:
                # No comment about the interviewer's comment
                    continue
                else:
                # Display comment in blue
                    with st.chat_message(message["role"], avatar=message["avatar"]):
                        st.markdown('<span style="color:blue">'+\
                                    message["content"] +\
                                    '</span>', unsafe_allow_html=True)
            else:
                with st.chat_message(message["role"], avatar=message["avatar"]):
                    st.markdown(message["content"])

        # User input: pinned to the bottom 
        if prompt := st.chat_input("Write your answer to the interviewer"):
            # Display user message in chat message container
            st.chat_message("applicant", avatar= "👨‍💼").markdown(prompt) 
            st.session_state.sim_messages.append({"role": "applicant", "avatar": "👨‍💼",
                                                  "content": prompt})

        # First: AI asks some interview question
        if st.session_state.sim_messages == []: # First question
            int_question = cp.generate_interview_question(cp.check_and_summarize_job(st.session_state,
                                                                                     char_lim=20000, # Can accept longer job desc 
                                                                                     verbose=False),
                                                          st.session_state.sim_messages)
            st.chat_message("interviewer", avatar= "🕵️‍♂️").markdown(int_question) 
            st.session_state.sim_messages.append({"role": "interviewer", "avatar": "🕵️‍♂️", 
                                                  "content": int_question})
        elif st.session_state.sim_messages[-1]['role'] == 'applicant': # Last comment is by applicant 
            int_comment = cp.generate_interview_comment(st.session_state.sim_messages)
            if st.session_state['int_sim_toggle_comment'] == True: # Display comment in blue, if toggled
                st.chat_message("tacit_commenter", avatar= "📋").\
                    markdown('<span style="color:blue">'+ int_comment +\
                             '</span>', unsafe_allow_html=True)
            st.session_state.sim_messages.append({"role": "tacit_commenter", "avatar": "📋", 
                                                  "content": int_comment})            
            int_question = cp.generate_interview_followup(int_comment, st.session_state.sim_messages)
            st.chat_message("interviewer", avatar= "🕵️‍♂️").markdown(int_question) 
            st.session_state.sim_messages.append({"role": "interviewer", "avatar": "🕵️‍♂️", 
                                                  "content": int_question})
        else: 
            pass
            
        with st.sidebar:
            if st.button("Restart interview simulator", type="primary", use_container_width=True):
                st.session_state['int_sim_state'] = "initialize"
                st.rerun()
            # Button to toggle interviewer's commena and changing names
            if st.session_state['int_sim_toggle_comment'] == False:
                if st.button("Turn ON interviewer's comment", use_container_width=True):
                    st.session_state['int_sim_toggle_comment'] = True
                    st.rerun()
            else: 
                if st.button("Turn OFF interviewer's comment", use_container_width=True):
                    st.session_state['int_sim_toggle_comment'] = False
                    st.rerun()
            st.markdown("### AI Answer Assist")
            if st.button("Generate a short reply", use_container_width=True): 
                ai_answer = cp.generate_interview_answer(st.session_state['resume_text_original'],
                                                         st.session_state.sim_messages)
                st.chat_message("applicant", avatar= "👨‍💼").markdown(prompt) 
                st.session_state.sim_messages.append({"role": "applicant", "avatar": "👨‍💼",
                                                      "content": ai_answer})
                st.rerun()
            if st.button("Generate a detailed reply", use_container_width=True): 
                ai_answer = cp.generate_interview_answer(st.session_state['resume_text_original'],
                                                         st.session_state.sim_messages, short=False)
                st.chat_message("applicant", avatar= "👨‍💼").markdown(prompt) 
                st.session_state.sim_messages.append({"role": "applicant", "avatar": "👨‍💼",
                                                      "content": ai_answer})
                st.rerun()
            
    case "interviewer":
        # Display chat messages 
        for message in st.session_state.sim_messages:
            if message['role'] == "tacit_commenter":
                if st.session_state['int_sim_toggle_comment'] == False:
                # No comment about the interviewer's comment
                    continue
                else:
                # Display comment in blue
                    with st.chat_message(message["role"], avatar=message["avatar"]):
                        st.markdown('<span style="color:blue">'+\
                                    message["content"] +\
                                    '</span>', unsafe_allow_html=True)
            else:
                with st.chat_message(message["role"], avatar=message["avatar"]):
                    st.markdown(message["content"])

        # User input (interview question): pinned to the bottom 
        if prompt := st.chat_input("Write your question to the candidate"):
            # Display user message in chat message container
            st.chat_message("interviewer", avatar= "🕵️‍♂️").markdown(prompt)
            st.session_state.sim_messages.append({"role": "interviewer", "avatar": "🕵️‍♂️", 
                                                  "content": prompt})

        # AI give some response
        if st.session_state.sim_messages != []:
            print (st.session_state.sim_messages)
            if st.session_state.sim_messages[-1]['role'] == 'interviewer': # Last comment is by applicant 
                int_answer = cp.generate_interview_answer(st.session_state['resume_text_original'],
                                                            st.session_state.sim_messages)
                st.chat_message("applicant", avatar= "👨‍💼").markdown(int_answer) 
                st.session_state.sim_messages.append({"role": "applicant", "avatar": "👨‍💼", 
                                                    "content": int_answer})
        else: 
            pass
            
        with st.sidebar:
            if st.button("Restart interview simulator", type="primary", use_container_width=True):
                st.session_state['int_sim_state'] = "initialize"
                st.rerun()
            st.markdown("### AI Question Assist")
            if st.button("Generate a new question", use_container_width=True): 
                ai_question = cp.generate_interview_question(cp.check_and_summarize_job(st.session_state,
                                                                                        char_lim=20000, # Can accept longer job desc 
                                                                                        verbose=False),
                                                             st.session_state.sim_messages)
                st.chat_message("interviewer", avatar= "🕵️‍♂️").markdown(ai_question) 
                st.session_state.sim_messages.append({"role": "interviewer", "avatar": "🕵️‍♂️", 
                                                      "content": ai_question})
                st.rerun()
            if st.session_state.sim_messages != []:
                if st.button("Generate a follow up question", use_container_width=True): 
                    ai_question = cp.generate_interview_followup("Candidate's response is satisfactory", # AI answer, assume satisfactory
                                                                  st.session_state.sim_messages)
                    st.chat_message("interviewer", avatar= "🕵️‍♂️").markdown(ai_question) 
                    st.session_state.sim_messages.append({"role": "interviewer", "avatar": "🕵️‍♂️", 
                                                        "content": ai_question})
                    st.rerun()
        pass

    case _:
        st.warning("Error found in the session_state")
