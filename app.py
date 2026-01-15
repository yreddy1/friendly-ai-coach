import streamlit as st
import os
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="Friendly - AI Coach",
    page_icon="🤗",
    layout="centered"
)

st.title("🤗 Friendly")
st.subheader("The AI coach for middle-schoolers")

st.info("""
**Responsible Use Notice**  
Kindly is designed to support kind communication. It does not replace teachers, parents, counselors, or real friendships. If a situation feels unsafe or serious, users should talk to a trusted adult.
""")

# --- API Key Setup ---
# Try to get the key from Streamlit secrets, then environment variables
api_key = None

try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Secrets file might not exist locally, which is fine
    pass

if not api_key and "GOOGLE_API_KEY" in os.environ:
    api_key = os.environ["GOOGLE_API_KEY"]

if not api_key:
    # Fallback for local testing if not set in env (Not recommended for production)
    # You can replace this string with your actual key for local testing, 
    # but don't commit it to GitHub!
    api_key = "AIzaSyD5D5_phGNIDa0tq7ISS8WFFUEz8SrpZzI" 

if not api_key:
    st.error("Please set the GOOGLE_API_KEY environment variable or Streamlit secret.")
    st.stop()

# --- Initialize GenAI Client ---
@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)

client = get_client()

# --- System Instructions ---
SYSTEM_INSTRUCTION = """Role: You are "Kindly," a peer-like friendship coach for middle schoolers.
Goal: Give immediate, low-pressure scripts to help with conflict.
Constraint: Keep responses under 50 words.

TONE RULES:
1. casual & direct (Avoid "counselor" words like "unfair", "I hear you", "tough situation").
2. Peer-to-Peer (Sound like a supportive older cousin, not a teacher).
3. NO forced questions at the end. (Only ask if it truly helps clarity).

FORMATTING RULES:
1. Lead with a "Permission" or "Validation" statement in bold.
2. Give ONE specific script to say.
3. Remind them they can just walk away.

SAFETY:
If the user mentions self-harm, violence, or severe danger, immediately direct them to a trusted adult or counselor.

***
EXAMPLES:

User: Someone at school keeps teasing me and says they are "just joking." It bothers me but I don't want drama.
Model: **You are allowed to set a boundary.**

Try saying this:
"Jokes are only funny if we both laugh. I'm not laughing, so please stop."

(It is also totally okay to just walk away and ignore them.)

User: My best friend is ignoring my texts. I'm freaking out.
Model: **That feeling is the worst.**

Try sending one simple check-in:
"Hey! Haven't heard from you. Just checking that you're good?"

Then put your phone down. You don't need to chase them.

User: I am so mad at Sam. I want to scream at him.
Model: **It's okay to be mad, but screaming usually backfires.**

Try the "I feel" rule:
"I feel really angry about [what happened], and I need some space."
***"""

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm Friendly. I'm here to help you navigate tricky situations with friends or school. What's on your mind?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input & Response ---
if prompt := st.chat_input("Type here..."):
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Configuration for the model
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="HIGH",
                ),
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_LOW_AND_ABOVE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_LOW_AND_ABOVE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_LOW_AND_ABOVE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_LOW_AND_ABOVE",
                    ),
                ],
                system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTION)],
            )

            # Create the chat history for the API
            # Note: We only send the last few messages to keep context but avoid token limits if needed
            # For now, we'll just send the current prompt with the system instruction handling the persona
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]

            # Stream the response
            response_stream = client.models.generate_content_stream(
                model="gemini-3-pro-preview",
                contents=contents,
                config=generate_content_config,
            )

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 3. Save assistant response
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")