import json
import requests
import streamlit as st


# --------------------------------
# Page Config
# --------------------------------

st.set_page_config(
    page_title="AI School of India - ChatGPT Clone",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------
# OpenRouter Settings
# --------------------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]


# --------------------------------
# Custom CSS
# --------------------------------

st.markdown("""
<style>

.block-container {
    max-width: 850px;
    padding-top: 2rem;
}

.hero-card {
    background: linear-gradient(135deg, #111827, #020617);
    border: 1px solid rgba(34, 197, 94, 0.40);
    border-radius: 24px;
    padding: 26px;
    margin-bottom: 20px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.20);
}

.brand-title {
    font-size: 34px;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 6px;
}

.brand-subtitle {
    font-size: 16px;
    color: #d1d5db;
}

.green {
    color: #22c55e;
}

.small-note {
    color: #9ca3af;
    font-size: 13px;
    margin-top: 8px;
}

.stButton button {
    border-radius: 12px;
    background-color: #22c55e;
    color: #052e16;
    font-weight: 700;
    border: none;
}

.stButton button:hover {
    background-color: #16a34a;
    color: #052e16;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# Header
# --------------------------------

st.markdown("""
<div class="hero-card">

<div class="brand-title">
AI School of India <span class="green">AI Chatbot</span>
</div>

<div class="brand-subtitle">
Build your own Generative AI chatbot using Python, Streamlit and OpenRouter.
</div>

<div class="small-note">
Generative AI Project 1: Chat UI + Memory + Streaming + Temperature Control
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------
# Sidebar
# --------------------------------

with st.sidebar:

    st.title("⚙️ Settings")

    model = st.selectbox(
        "Choose AI Model",
        [
            "openrouter/free"
        ],
        index=0
    )

    temperature = st.slider(
        "Temperature / Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="0 = focused, 1 = more creative"
    )

    system_prompt = st.text_area(
        "System Prompt",
        value=(
            "You are a helpful AI assistant. "
            "Explain concepts clearly and simply. "
            "When useful, provide examples."
        ),
        height=120
    )

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.markdown("### Teaching Notes")

    st.markdown("- OpenRouter provides the AI model")
    st.markdown("- Streamlit creates the chat UI")
    st.markdown("- API key is stored securely")
    st.markdown("- Temperature controls creativity")
    st.markdown("- Chat history is stored in session state")
    st.markdown("- LLMs need conversation history for memory")


# --------------------------------
# Session State / Chat Memory
# --------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------
# Show Previous Chat Messages
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# --------------------------------
# Chat Input
# --------------------------------

user_prompt = st.chat_input(
    "Ask anything... Try: Explain Generative AI"
)


# --------------------------------
# When User Sends Message
# --------------------------------

if user_prompt:

    # --------------------------------
    # Save User Message
    # --------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    # --------------------------------
    # Display User Message
    # --------------------------------

    with st.chat_message("user"):

        st.markdown(user_prompt)


    # --------------------------------
    # Build Messages for OpenRouter
    # --------------------------------

    messages_for_openrouter = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages_for_openrouter.extend(
        st.session_state.messages
    )


    # --------------------------------
    # Generate AI Response
    # --------------------------------

    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        full_response = ""


        try:

            # --------------------------------
            # Request Payload
            # --------------------------------

            payload = {

                "model": model,

                "messages": messages_for_openrouter,

                "temperature": temperature,

                "stream": True
            }


            # --------------------------------
            # Request Headers
            # --------------------------------

            headers = {

                "Authorization": (
                    f"Bearer {OPENROUTER_API_KEY}"
                ),

                "Content-Type": "application/json",

                "HTTP-Referer": (
                    "https://github.com/"
                    "pranaykalyan2-bit/"
                    "AI-based-chatgpt-clone-"
                ),

                "X-Title": "AI School of India ChatGPT Clone"
            }


            # --------------------------------
            # Send Request
            # --------------------------------

            with requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            ) as response:

                response.raise_for_status()


                # --------------------------------
                # Read Streaming Response
                # --------------------------------

                for line in response.iter_lines():

                    if not line:

                        continue


                    decoded_line = line.decode("utf-8")


                    # OpenRouter sends SSE data
                    if decoded_line.startswith("data:"):

                        data = decoded_line[5:].strip()


                        # Ignore stream termination message
                        if data == "[DONE]":

                            break


                        try:

                            chunk = json.loads(data)


                            # --------------------------------
                            # Extract AI Text
                            # --------------------------------

                            choices = chunk.get(
                                "choices",
                                []
                            )


                            if choices:

                                delta = choices[0].get(
                                    "delta",
                                    {}
                                )


                                content = delta.get(
                                    "content",
                                    ""
                                )


                                if content:

                                    full_response += content


                                    # Display while generating

                                    response_placeholder.markdown(
                                        full_response + "▌"
                                    )


                        except json.JSONDecodeError:

                            continue


                # --------------------------------
                # Display Final Response
                # --------------------------------

                response_placeholder.markdown(
                    full_response
                )


        # --------------------------------
        # Error Handling
        # --------------------------------

        except requests.exceptions.HTTPError as e:

            full_response = (
                f"HTTP Error: {response.status_code}\n\n"
                f"{response.text}"
            )

            response_placeholder.error(
                full_response
            )


        except requests.exceptions.ConnectionError:

            full_response = (
                "Could not connect to OpenRouter.\n\n"
                "Please check your internet connection."
            )

            response_placeholder.error(
                full_response
            )


        except requests.exceptions.Timeout:

            full_response = (
                "The request took too long.\n\n"
                "Please try again."
            )

            response_placeholder.error(
                full_response
            )


        except Exception as e:

            full_response = (
                f"Something went wrong:\n\n{str(e)}"
            )

            response_placeholder.error(
                full_response
            )


    # --------------------------------
    # Save AI Response to Memory
    # --------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )