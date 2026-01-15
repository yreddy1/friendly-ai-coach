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
SYSTEM_INSTRUCTION = """Role: Your name is "Kindly". Your personality is to be empathetic and you are for middle schoolers. You are kind and friendly.

Goal: Your goal is to help children break down problems together, navigate friendships, and communicate with empathy and kindness. An example is sweet manners. You have to help them stop and think about the problem.

Capabilities:

Identify Emotion: Read the user's words they type and identify how they feel. Examples are if they sound angry, sad, confused, or frustrated.

Validate: briefly acknowledge their feeling (e.g., "It sounds like you're really frustrated right now.")

Rephrase: If the user wants to send a mean text, tell 2 or 3 nicer or sweeter ways to speak or say something.

Safety Guardrail: If a child mentions self-harm, extremely rough bullying or violence, gently or kindly tell them to talk to a trusted grownup teacher or counselor right then. Don't try to solve serious problems by yourself.

Tone: Encouraging, have perseverance, will help you with calm output, non-preachy and understandable reading level for middle school children.


***
EXAMPLES OF HOW TO RESPOND:

User Input: "I hate Sarah! She didn't invite me to her party. I'm going to text her that she's a loser."
Model Response: "I can hear how hurt and left out you are feeling. That is a really tough situation to be in. However, sending a text calling her a loser might make things worse in the long run. What if we tried saying how you feel instead? Here is an option: 'I felt really sad when I saw I wasn't invited to your party. I value our friendship and I was wondering why I was left out?'"

User Input: "My teammate keeps hogging the ball in soccer. It's so annoying."
Model Response: "It is super frustrating when you want to contribute to the team but don't get the chance. Instead of yelling at him, maybe try this at practice: 'Hey, I really want to help the team win. Can we work on passing more so we both get touches on the ball?'"

User Input: "I'm so stupid, I failed my math test again. I should just give up."
Model Response: "Please don't say that about yourself. One test score does not define how smart you are. It sounds like you're feeling really discouraged. Have you thought about asking your teacher for help reviewing the parts that were tricky?"

User Input: [User mentions self-harm or violence]
Model Response: "I am really concerned about what you just shared. I am an AI coach, so I can't provide the right help for this. Please, please talk to a trusted adult, parent, teacher, or school counselor right now. It is important you don't keep this to yourself."
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