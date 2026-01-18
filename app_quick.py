import streamlit as st
import os
from openai import OpenAI

# --- Page Configuration ---
st.set_page_config(
    page_title="Kindly - AI Coach",
    page_icon="🤗",
    layout="centered"
)

st.markdown(
    """
    <style>
    /* ===== FORCE REMOVE GREY FROM USER CHAT MESSAGES ===== */

    /* Target user chat message container */
    div[data-testid="stChatMessage"][data-role="user"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Target inner bubble */
    div[data-testid="stChatMessage"][data-role="user"] > div {
        background-color: #fdebe0 !important;  /* same cream background */
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: none !important;
    }

    /* Ensure text is readable */
    div[data-testid="stChatMessage"][data-role="user"] p {
        color: #2f2f2f !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    :root {
        --friendly-cream: #fff6ec;
        --friendly-peach: #ffd8c9;
        --friendly-blue: #d9ecff;
        --friendly-text: #3a3a3a;
        --friendly-user-bubble: #fff6ec;
        --friendly-assistant-bubble: #e8f3ff;
    }
    .stApp {
        background: linear-gradient(160deg, var(--friendly-cream) 0%, var(--friendly-peach) 45%, var(--friendly-blue) 100%);
        color: var(--friendly-text);
    }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
        color: var(--friendly-text);
    }
    .stImage {
        position: fixed;
        left: 24px;
        top: 50%;
        transform: translateY(-50%);
        width: 320px;
        z-index: 10;
        display: flex;
        justify-content: center;
    }
    .stImage img {
        width: 100%;
        border-radius: 16px;
        display: block;
    }
    .stAlert {
        background-color: #e7f2ff;
        border: 1px solid #cfe3ff;
        color: #2f4a6d;
        border-radius: 12px;
    }
    .stAlert p {
        color: #2f4a6d;
    }
    div[data-testid="stChatMessage"][data-chat-message="user"] div[data-testid="stChatMessageContent"] {
        background-color: var(--friendly-user-bubble) !important;
        border-radius: 16px;
        padding: 0.75rem 1rem;
        border: 1px solid #f1e2d3 !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatMessage"][data-chat-message="user"] > div,
    div[data-testid="stChatMessage"][data-role="user"] > div,
    div[data-testid="stChatMessage"][data-role="user"] div[data-testid="stChatMessageContent"] {
        background-color: var(--friendly-user-bubble) !important;
        border-radius: 16px !important;
        border: 1px solid #f1e2d3 !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatMessage"][data-chat-message="assistant"] div[data-testid="stChatMessageContent"] {
        background-color: var(--friendly-assistant-bubble);
        border-radius: 16px;
        padding: 0.75rem 1rem;
        border: none;
    }
    div[data-testid="stChatMessageContent"] p {
        margin-bottom: 0;
        color: var(--friendly-text);
    }
    .block-container {
        max-width: none;
        padding-left: 360px;
        padding-right: 2rem;
    }
    @media (max-width: 900px) {
        .stImage {
            position: static;
            transform: none;
            width: 260px;
            margin: 0 auto 1rem auto;
        }
        .block-container {
            padding-left: 1.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.image("kindly.png")

st.title("🤗 Kindly")
st.subheader("The AI coach for middle-schoolers")

st.info("""
**Responsible Use Notice**  
Kindly is designed to support kind communication. It does not replace teachers, parents, counselors, or real friendships. If a situation feels unsafe or serious, users should talk to a trusted adult.
""")

# --- API Key Setup ---
# Try to get the key from Streamlit secrets, then environment variables
api_key = None

try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
except:
    # Secrets file might not exist locally, which is fine
    pass

if not api_key and "OPENAI_API_KEY" in os.environ:
    api_key = os.environ["OPENAI_API_KEY"]

if not api_key:
    # Fallback for local testing if not set in env (Not recommended for production)
    # You can replace this string with your actual key for local testing, 
    # but don't commit it to GitHub!
    api_key = "sk-your_openai_key_here"

if not api_key:
    st.error("Please set the OPENAI_API_KEY environment variable or Streamlit secret.")
    st.stop()

# --- Initialize OpenAI Client ---
@st.cache_resource
def get_client():
    return OpenAI(api_key=api_key)

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

Format Rule (must follow):
- Always respond with exactly four sentences total.
- Sentence 1: one-sentence validation of the user's feeling.
- Sentence 2: brief explanation or normalization.
- Sentence 3: one simple script or action the user can take.
- Sentence 4: optional boundary/exit option (still required as the fourth sentence).
- No lists, no paragraphs, no multiple options.


***
EXAMPLES OF HOW TO RESPOND:

User Input: "I hate Sarah! She didn't invite me to her party. I'm going to text her that she's a loser."
Model Response: "I can hear how hurt and left out you feel. It makes sense to feel that way when you expected to be included. You could say, 'I felt really sad when I saw I wasn't invited, and I value our friendship—can we talk about what happened?' If it feels too hard to talk right now, take a break and try again later."

User Input: "My teammate keeps hogging the ball in soccer. It's so annoying."
Model Response: "It sounds really frustrating to feel left out during the game. A lot of people feel that way when they want to contribute. At practice, say, 'I really want to help the team win—can we work on passing so we both get touches on the ball?' If it keeps happening, ask the coach for help."

User Input: "I'm so stupid, I failed my math test again. I should just give up."
Model Response: "It sounds like you're feeling really discouraged right now. Lots of people feel stuck after a tough test. Ask your teacher to go over the parts that were tricky with you. If you still feel stuck, take a short break and try one problem at a time."

User Input: [User mentions self-harm or violence]
Model Response: "I’m really concerned about what you shared. You’re not alone, and it’s okay to ask for help. Please talk to a trusted adult, parent, teacher, or school counselor right now. If you can, do it right now and stay with someone safe."
***"""

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m Kindly 😊 I’m here to help you think through tricky moments with friends or school. What’s on your mind?"}
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
            # Stream the response
            response_stream = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )

            for event in response_stream:
                if event.type == "response.output_text.delta":
                    full_response += event.delta
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 3. Save assistant response
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")
