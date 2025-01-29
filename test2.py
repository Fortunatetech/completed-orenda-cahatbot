from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
# Title of the Streamlit app
st.title("Orenda Form Intake Assistance")

# Initialize the OpenAI client
client = OpenAI(api_key=key)

# Set the OpenAI model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize messages, progress tracking, and response storage
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to the Orenda Intake System! Let's get started with some questions to complete your intake form."}]

if "intake_complete" not in st.session_state:
    st.session_state.intake_complete = False

if "responses" not in st.session_state:
    st.session_state.responses = {}

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Define intake flow as context for the assistant
intake_context = """
- You are an interactive assistant helping with a patient intake form.
- Respond interactively, keeping the conversation friendly and professional.
- Confirm when all questions have been answered. And Thank the patient including their first name for completing the intake form and that their responses have been recorded that A member of our team will reach out to you as soon as possible for the next step.
- Validate all the patients response to match the require question lets date match date, email to match email and so on.
- Please ask the following questions one by one:
What is your first name?
And your last name?
How did you hear about us?
What is your date of birth? Please use the format MM/DD/YYYY.
Is this appointment for a minor child? 
What is your sex assigned at birth? 
Please enter your street address.
What city do you live in?
What state?
And your zip code?
What is your email address?
Can you share your telephone number?
"""

# Function to save responses to a text file
def save_responses_to_file(responses):
    file_path = "patient_intake_form.txt"
    with open(file_path, "w") as file:
        for question, answer in responses.items():
            file.write(f"{question}: {answer}\n")
    return file_path

# Handle user input
if prompt := st.chat_input("Your response here:"):
    # Append user response to messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the assistant's response using OpenAI chat model
    if not st.session_state.intake_complete:
        messages = [{"role": "system", "content": intake_context}] + st.session_state.messages
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            temperature=0.7
        )
        assistant_reply = response.choices[0].message.content

        # Save response if it matches a question
        for question in intake_context.splitlines():
            if question.strip() and question in assistant_reply:
                st.session_state.responses[question] = prompt

        # Check for completion of the intake process
        if "Your intake is now complete" in assistant_reply:
            st.session_state.intake_complete = True
            save_responses_to_file(st.session_state.responses)  # Save responses after completion
            st.success("Your responses have been saved successfully.")

        # Append assistant response to messages
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
    else:
        st.warning("The intake process is already complete.") 