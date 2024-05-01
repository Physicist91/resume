import streamlit as st
from PyPDF2 import PdfReader 
from pdfplumber import pdf

def load_split_pdf(file):
    pdf_loader = PdfReader(file)
    pdf_text = ""
    for page_num in range(len(pdf_loader.pages)):
        pdf_page = pdf_loader.pages[page_num]
        pdf_text += pdf_page.extract_text()
    return pdf_text

def check_completion():
    if st.session_state['resume_text_original'] is None:
        st.warning('Please upload your resume.', icon="⚠️")
    elif st.session_state['job_title'] == "":
        st.warning('Please input the job title.', icon="⚠️")
    elif st.session_state['company_name'] == "":
        st.warning('Please input the company name.', icon="⚠️")
    elif st.session_state['job_description'] == "":
        st.warning('Please input the job description.', icon="⚠️")
    else:
        st.session_state['form_filled'] = True
        return True

# Initialise session_state
if 'resume_text_original' not in st.session_state:
    st.session_state['resume_text_original'] = ""
if 'job_title' not in st.session_state:
    st.session_state['job_title'] = ""
if 'company_name' not in st.session_state:
    st.session_state['company_name'] = ""
if 'job_description' not in st.session_state:
    st.session_state['job_description'] = ""

# Set page title
st.set_page_config(page_title="Resumify by ANUKS")

st.markdown("# Resumify")
st.markdown("Version 0.1")
st.markdown("#### Enhance your resume and generate cover letter for your dream job!")
st.markdown("With the power of AI, you can tailor and personalize your resume and cover letter for your dream job.  \
            Upload and make your own persona, and the resume and cover letter **speak like yourself**.")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader("Upload your original resume here", type=['pdf'])
if uploaded_file:
    st.session_state['resume_text_original'] = load_split_pdf(uploaded_file)
    st.session_state['resume_filename'] = uploaded_file.name
    st.write("Resume uploaded and parsed:", st.session_state['resume_filename'])
elif st.session_state['resume_text_original'] != "":
    # Display previously uplaoded resume, if any
    st.write("Previously uploaded and parsed resume:", st.session_state['resume_filename'])

# Data input
st.session_state['job_title'] = st.text_input('Job title', value=st.session_state['job_title'], 
                                              placeholder='Senior Executive Director')
st.session_state['company_name'] = st.text_input('Company name', value=st.session_state['company_name'], 
                                                 placeholder='FAANG Limited')
st.session_state['job_description'] = st.text_area('Job description', value=st.session_state['job_description'], 
                                                   placeholder="Responsibilities, requirements, etc (just copy paste lah)")

# Submission buttons
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Enhance resume", use_container_width=True):
        # Check whether all fields have been filled
        if check_completion():
            st.session_state['res_enh_state'] = "initialize"
            st.switch_page('pages/1 Resume Enhancer.py')
with col2:
    if st.button("Generate cover letter", use_container_width=True):
        # Check whether all fields have been filled
        if check_completion():
            st.switch_page('pages/2 Cover Letter Generator.py')
with col3:
    if st.button("Interview simulator", use_container_width=True):
        # Check whether all fields have been filled
        if check_completion():
            st.switch_page('pages/3 Interview Simulator.py')
