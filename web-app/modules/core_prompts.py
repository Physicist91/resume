import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

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
