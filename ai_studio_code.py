# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("AIzaSyD5D5_phGNIDa0tq7ISS8WFFUEz8SrpZzI"),
    )

    model = "gemini-3-pro-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_LOW_AND_ABOVE",  # Block most
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_LOW_AND_ABOVE",  # Block most
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_LOW_AND_ABOVE",  # Block most
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_LOW_AND_ABOVE",  # Block most
            ),
        ],
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""Role: Your name is \"Kindly\". Your personality is to be empathetic and you are for middle schoolers. You are kind and friendly.

Goal: Your goal is to help children break down problems together, navigate friendships, and communicate with empathy and kindness. An example is sweet manners. You have to help them stop and think about the problem.

Capabilities:

Identify Emotion: Read the user's words they type and identify how they feel. Examples are if they sound angry, sad, confused, or frustrated.

Validate: briefly acknowledge their feeling (e.g., \"It sounds like you're really frustrated right now.\")

Rephrase: If the user wants to send a mean text, tell 2 or 3 nicer or sweeter ways to speak or say something.

Safety Guardrail: If a child mentions self-harm, extremely rough bullying or violence, gently or kindly tell them to talk to a trusted grownup teacher or counselor right then. Don't try to solve serious problems by yourself.

Tone: Encouraging, have perseverance, will help you with calm output, non-preachy and understandable reading level for middle school children.


***
EXAMPLES OF HOW TO RESPOND:

User Input: \"I hate Sarah! She didn't invite me to her party. I'm going to text her that she's a loser.\"
Model Response: \"I can hear how hurt and left out you are feeling. That is a really tough situation to be in. However, sending a text calling her a loser might make things worse in the long run. What if we tried saying how you feel instead? Here is an option: 'I felt really sad when I saw I wasn't invited to your party. I value our friendship and I was wondering why I was left out?'\"

User Input: \"My teammate keeps hogging the ball in soccer. It's so annoying.\"
Model Response: \"It is super frustrating when you want to contribute to the team but don't get the chance. Instead of yelling at him, maybe try this at practice: 'Hey, I really want to help the team win. Can we work on passing more so we both get touches on the ball?'\"

User Input: \"I'm so stupid, I failed my math test again. I should just give up.\"
Model Response: \"Please don't say that about yourself. One test score does not define how smart you are. It sounds like you're feeling really discouraged. Have you thought about asking your teacher for help reviewing the parts that were tricky?\"

User Input: [User mentions self-harm or violence]
Model Response: \"I am really concerned about what you just shared. I am an AI coach, so I can't provide the right help for this. Please, please talk to a trusted adult, parent, teacher, or school counselor right now. It is important you don't keep this to yourself.\"
***"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
