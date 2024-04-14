import streamlit as st
from modules import core_prompts as cp
from modules import gif_generator as gg
from modules import formatter as fmt

# Set page title
st.set_page_config(page_title="Resume Enhancer by ANUKS")

# Initialise session_state
if 'res_enh_state' not in st.session_state:
    # State of the webpage
    # 1. initialize - initial condition of the webpage
    # 2. processing - processing the data, and generate a response
    # 3. resume_ready - resume is generated
    st.session_state['res_enh_state'] = "initialize"

match st.session_state['res_enh_state']:
     
    case "initialize":
        # The initial form of the webpage
        if "form_filled" not in st.session_state:
            st.markdown("## Resume Enhancer")
            st.warning('Please input and submit the form in the home page.', icon="⚠️")
            if st.button("Go back to home"):
                st.switch_page('0 Home.py')
        else:
            # Go to processing 
            st.session_state['res_enh_state'] = "processing"
            st.rerun()

    case "processing":
        # Processing the data
        st.markdown("## Resume Enhancer")
        job_desc = cp.check_and_summarize_job(st.session_state)
        st.write("Your dream resume will be here in just a few seconds...")

        # Gif generator 
        gif_url = gg.generate_random_gif()
        if gif_url:
            st.markdown("For now, here is a random gif for you: ")
            st.markdown("![Some random job gif :)]({})".format(gif_url))

        # Processing resume
        resume_text_generated = cp.enhance_resume(st.session_state['resume_text_original'], job_desc)
        st.session_state['resume_text'] = resume_text_generated
        st.session_state['res_enh_state'] = "resume_ready"
        st.rerun()

    case "resume_ready":
        st.markdown(st.session_state['resume_text'])
        with st.sidebar:
            st.markdown("### Customization")
            if st.button("Edit Resume Text"):
                st.session_state['res_enh_state'] = "resume_text_edit"
                st.rerun()
            st.download_button(label="Save as Markdown",
                               data=st.session_state['resume_text'],
                               file_name='resume.md',
                               mime='text/markdown')
            st.download_button(label="Save as PDF",
                               data=fmt.convert_pdf(st.session_state['resume_text']),
                               file_name='resume.pdf',
                               mime='pdf')
            if st.button("Regenerate Resume"):
                st.session_state['res_enh_state'] = "initialize"
                st.rerun()

    case "resume_text_edit":
        st.session_state['resume_text'] = st.text_area(label="Resume markdown text:",
                                                       value = st.session_state['resume_text'],
                                                       height = 500)
        with st.sidebar:
            st.markdown("### Customization")
            if st.button("Finish editing"):
                st.session_state['res_enh_state'] = "resume_ready"
                st.rerun()

    case _:
        st.warning("Error found in the session_state")


