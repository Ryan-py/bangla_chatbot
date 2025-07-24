import streamlit as st
import google.generativeai as genai

# --- System Instructions (in English) ---
SYSTEM_INSTRUCTION_EN = """
You are a helpful and informative AI assistant.
You have been provided with the following context. Use this context to answer the user's questions.
If you cannot find the answer within the provided context, state that you do not have information on that specific topic.
Respond in Bengali.

Provided Information (Context):
{knowledge_base_content}
"""

# --- Configuration for Gemini API Key ---
# Store your Gemini API key in .streamlit/secrets.toml like this:
# GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
# Streamlit will automatically load it.
try:
    gemini_api_key = st.secrets["GEMINI_API"]
    genai.configure(api_key=gemini_api_key)
except KeyError:
    st.error(
        "Gemini API Key not found. "
        "Please add it to your Streamlit secrets (`.streamlit/secrets.toml`). "
        "Instructions: https://docs.streamlit.io/develop/concepts/connections/secrets-management"
    )
    st.stop() # Stop the app if API key is not found

# --- Chatbot Setup ---
st.title("💬 Bengali Gemini Chatbot") # English title
st.write(
    "This is a simple chatbot that uses Google's Gemini Pro model. "
    "Please ask your questions in Bengali."
)

# You can put your "knowledge base" content here directly.
# For a PoC, keep it concise.
BANGLA_KNOWLEDGE_BASE = """
বাংলাদেশের জাতীয় ফল কাঁঠাল। কাঁঠাল আকারে বেশ বড় হয় এবং এর পুষ্টিগুণ অনেক। এটি গ্রীষ্মকালে পাওয়া যায়।
বাংলাদেশের রাজধানী ঢাকা। এটি একটি জনবহুল শহর।
জাতীয় ফুল শাপলা।
বাংলাদেশের প্রধান ভাষা বাংলা।
"""

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field.
if prompt := st.chat_input("Write your question in Bengali..."): # English prompt text

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construct the full prompt for this turn, including the system instruction and knowledge base.
    combined_prompt = SYSTEM_INSTRUCTION_EN.format(knowledge_base_content=BANGLA_KNOWLEDGE_BASE) + \
                      f"\n\nUser's Question: {prompt}"

    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-pro')

    with st.spinner("Thinking..."): # English spinner text
        try:
            # Generate a response using the Gemini API.
            response_stream = model.generate_content(
                combined_prompt,
                stream=True,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )

            # Stream the response to the chat using `st.write_stream`.
            full_gemini_response = ""
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                for chunk in response_stream:
                    full_gemini_response += chunk.text
                    response_placeholder.markdown(full_gemini_response + "▌") # Add a blinking cursor effect
                response_placeholder.markdown(full_gemini_response) # Remove cursor at the end

            # Store the full response in session state.
            st.session_state.messages.append({"role": "assistant", "content": full_gemini_response})

        except Exception as e:
            st.error(f"Sorry, an error occurred: {e}") # English error message
            st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})