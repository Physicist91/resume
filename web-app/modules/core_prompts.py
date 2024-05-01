import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load AI model
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
model = ChatGoogleGenerativeAI(model="gemini-pro")

def check_and_summarize_job(session_data, char_lim=2000, verbose=True):
    # Check length and summarize job if exceeds length 
    job_desc= "Job title: {} \nCompany name: {}\nJob description: {}".\
        format(session_data['job_title'], session_data['company_name'], session_data['job_description'])
    if len(job_desc) > char_lim:
        if verbose:
            st.write("Job description is too long. Summarizing (takes a few seconds)...")
        summarize_job(job_desc)
    else:
        return job_desc

def summarize_job(job_desc):
    prompt = ChatPromptTemplate.from_template("Summarize the following job description {job_desc}")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    job_summ = chain.invoke({"job_desc": job_desc})
    return job_summ

def enhance_resume(resume_text, job_desc):
    prompt = ChatPromptTemplate.from_template("Make a personalized resume with the following resume {resume_text},\
                                              to apply to a job with a description {job_desc}.\
                                              Please stay truthful to the given information, and do not make up numbers.\
                                              Give a markdown line break to delineate each section.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    resume_new = chain.invoke({"job_desc": job_desc, "resume_text": resume_text})
    return resume_new

def generate_cover_letter(resume_text, job_desc):
    prompt = ChatPromptTemplate.from_template("Make a personalized cover letter with the following resume {resume_text},\
                                              to apply to a job with a description {job_desc},\
                                              highlighting relevant information.\
                                              Please stay truthful to the given information, and do not make up numbers.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    cover_letter = chain.invoke({"job_desc": job_desc, "resume_text": resume_text})
    return cover_letter

def rephrase_text(rephrase_text, rephrase_instruction):
    if rephrase_instruction == "":
        # Empty instruction
        prompt = ChatPromptTemplate.from_template("Please rephrase the following sentence: {sentence}")
        output_parser = StrOutputParser()
        chain = prompt | model | output_parser
        result = chain.invoke({"sentence": rephrase_text})
    else:
        # With instruction
        prompt = ChatPromptTemplate.from_template("Please rephrase the following sentence, making it {instruction}: {sentence}")
        output_parser = StrOutputParser()
        chain = prompt | model | output_parser
        result = chain.invoke({"sentence": rephrase_text, "instruction": rephrase_instruction})
    return result

def chat_history_as_string(chat_history):
    chat_history_str = ""
    for chat in chat_history:
        line_str =  chat['role'] + " : " + chat['content'] + "\n"
        chat_history_str = chat_history_str + line_str 
    return chat_history_str

def generate_interview_question(job_description, chat_history):
    interview_exchange = chat_history_as_string(chat_history)
    prompt = ChatPromptTemplate.from_template("You are a part of an expert interview panel,\
                                              looking for a candidate satisfying the following job description:\n\
                                              {job_description}\n\n\
                                              With a recent interview conversation as follow:\n\
                                              {interview_exchange}\n\
                                              ask ONE NEW question IMMEDIATELY as a panel. Do not use any symbol.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"job_description": job_description, "interview_exchange": interview_exchange})
    return result

def generate_interview_comment(chat_history):
    interview_exchange = chat_history_as_string(chat_history)
    prompt = ChatPromptTemplate.from_template("You are a part of an expert interview panel.\n\
                                              With a recent interview conversation as follow:\n\
                                              {interview_exchange}\n\
                                              Reflecting on the candidate's last answer,\
                                              give a comment whether the candidate response is satisfactory.\n\
                                              Give a stern comment if candidate response is empty, nonsensical or too short.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"interview_exchange": interview_exchange})
    return result

def generate_interview_followup(interview_comment, chat_history):
    interview_exchange = chat_history_as_string(chat_history)
    prompt = ChatPromptTemplate.from_template("You are a part of an expert interviewer panel.\n\
                                              With the comment from the lead interviewer to the candidate's last answer as follow:\n\
                                              {interview_comment}\n\
                                              and a recent interview conversation as follow:\n\
                                              {interview_exchange}\n\
                                              Generate a SHORT and TACTFUL response to the candidate, ending with a question.\n\
                                              Do not use any symbol.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"interview_comment": interview_comment, "interview_exchange": interview_exchange})
    return result

def generate_interview_answer(resume_text, chat_history, short=True):
    interview_exchange = chat_history_as_string(chat_history)
    length = "SHORT" if short==True else "DETAILED"
    prompt = ChatPromptTemplate.from_template("You are an expert job candidate with following resume:\n\
                                              {resume_text}\n\n\
                                              With a recent interview conversation as follow:\n\
                                              {interview_exchange}\n\
                                              craft a tactful {length} response to the interviewer's question. Do not use any symbol.")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"resume_text": resume_text, "interview_exchange": interview_exchange, "length": length})
    return result
