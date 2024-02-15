import streamlit as st
# import google.generativeai as genai
from langchain.chat_models import ChatOpenAI
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate

# Load environment variables from a .env file
load_dotenv()

def generate_response(input_text):
     # Create a GenerativeModel instance with 'OpenAI' as the model type
    llm=ChatOpenAI(temperature=0.0,openai_api_key=api_key)
    # Generate content based on the input text
    output = llm(input_text)
    # Return the generated text
    return output.content

def extract_text_from_pdf_file(uploaded_file):
    # Use PdfReader to read the text content from a PDF file
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

def extract_text_from_docx_file(uploaded_file):
    # Use docx2txt to extract text from a DOCX file
    return docx2txt.process(uploaded_file)

# Prompt Template
input_prompt_template = """
As an experienced Applicant Tracking System (ATS) analyst,
with profound knowledge in technology, software engineering, data science, 
and big data engineering, your role involves evaluating resumes against job descriptions.
Recognizing the competitive job market, provide top-notch assistance for resume improvement.
Your goal is to analyze the resume against the given job description, 
assign a percentage match based on key criteria, and pinpoint missing keywords accurately.

Resume: {text}
Job Description: {job_description}

I want the response in one single string, structured as:
{{
  "Candidate Name": "",
  "Job Description Match": "%",
  "Missing Keywords": "",
  "Candidate Summary": "",
  "Experience": "",
  "Education": "",
  "Skills Assessment": "",
  "Industry Relevance": "",
  "Custom Feedback": ""
}}

Ensure detailed and accurate information, as hiring decisions depend on your analysis. Present each response element with comprehensive details. Give Job description match percentage after thorough analysis of the resume against the requirements.
"""

prompt_template = ChatPromptTemplate.from_template(input_prompt_template)

# Streamlit app
st.set_page_config(page_title="Intelligent ATS System", layout="wide")


# Sidebar for API Key
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Input API Key", type="password")

if api_key:
    
    job_description = st.text_area("Job Description", height=300)

    # File Uploader
    uploaded_files = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True, help="Upload PDF or DOCX files")

    # Submit Button
    submit_button = st.button("Analyze Resumes")


    if submit_button and uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            resume_text = ""
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf_file(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx_file(uploaded_file)

            response_text = generate_response(prompt_template.format_messages(text=resume_text, job_description=job_description))
            response_dict = eval(response_text)

            st.subheader(f"ATS Evaluation Result for {response_dict['Candidate Name']}:")
            st.markdown(f"**Job Description Match:** {response_dict['Job Description Match']}")
            st.markdown(f"**Missing Keywords:** {response_dict['Missing Keywords']}")
            st.markdown("**Candidate Summary:**")
            st.write(response_dict['Candidate Summary'])
            st.markdown("**Experience:**")
            st.write(response_dict['Experience'])

            # New Fields
            st.markdown("**Education:**")
            st.write(response_dict['Education'])
            st.markdown("**Skills Assessment:**")
            st.write(response_dict['Skills Assessment'])
            st.markdown("**Industry Relevance:**")
            st.write(response_dict['Industry Relevance'])
            st.markdown("**Custom Feedback:**")
            st.write(response_dict['Custom Feedback'])

            match_percentage = float(response_dict['Job Description Match'].rstrip('%'))
            if match_percentage >= 80:
                st.success(f"{file_name}: Move forward with hiring!")
            else:
                st.error(f"{file_name}: Needs Improvement")