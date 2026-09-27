import json
import requests
import streamlit as st


# --------------------------------
# Page Config
# --------------------------------

st.set_page_config(
    page_title="My Local ChatGPT Clone",
    page_icon="🤖",
    layout="centered"
)


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
My Local ChatGPT Clone <span class="green">Local AI Chatbot</span>
</div>

<div class="brand-subtitle">
My First Generative AI app using Python, Streamlit and Ollama — no OpenAI credits required.
</div>

<div class="small-note">
Generative AI Project 1: Chat UI + Memory + Streaming + Temperature Control using local models
</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------
# Ollama Settings
# --------------------------------

OLLAMA_URL = "http://localhost:11434/api/chat"


# --------------------------------
# Sidebar
# --------------------------------

with st.sidebar:

    st.title("⚙️ Settings")

    model = st.selectbox(
        "Choose Ollama Model",
        [
            "llama3.2",
            "llama3.1",
            "llama3",
            "mistral",
            "gemma2",
            "qwen2.5",
            "qwen2.5:3b"
        ],
        index=0
    )

    temperature = st.slider(
        "Temperature / Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="0 = focused/robotic, 1 = creative"
    )

    system_prompt = st.text_area(
        "System Prompt",
        value=(
            "You are a helpful AI assistant. "
            "Explain concepts clearly and simply. "
            "When useful, respond with examples."
        ),
        height=120
    )

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.markdown("### Teaching Notes")

    st.markdown("- Ollama runs model locally")
    st.markdown("- No OpenAI credits needed")
    st.markdown("- Token = word chunk")
    st.markdown("- Temperature = creativity dial")
    st.markdown("- LLMs are stateless unless we send history")


# --------------------------------
# Helper Function
# --------------------------------

def check_ollama_running():

    try:

        response = requests.get(
            "http://localhost:11434",
            timeout=3
        )

        return response.status_code == 200

    except requests.exceptions.RequestException:

        return False


# --------------------------------
# Session State / Memory
# --------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------
# Ollama Health Check
# --------------------------------

if not check_ollama_running():

    st.error("❌ Ollama is not running.")

    st.info(
        "Open the Ollama application and try again."
    )

    st.stop()


# --------------------------------
# Show Chat History
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# --------------------------------
# Chat Input
# --------------------------------

user_prompt = st.chat_input(
    "Ask anything... Try Telugu also: 'Generative AI ante enti?'"
)


# --------------------------------
# When User Sends Message
# --------------------------------

if user_prompt:

    # 1. Save user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    # 2. Display user message

    with st.chat_message("user"):

        st.markdown(user_prompt)


    # 3. Build messages for Ollama

    messages_for_ollama = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages_for_ollama.extend(
        st.session_state.messages
    )


    # 4. Generate AI response

    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        full_response = ""


        try:

            payload = {

                "model": model,

                "messages": messages_for_ollama,

                "stream": True,

                "options": {
                    "temperature": temperature
                }
            }


            # Send request to Ollama

            with requests.post(
                OLLAMA_URL,
                json=payload,
                stream=True,
                timeout=120
            ) as response:

                response.raise_for_status()


                # Read streaming response

                for line in response.iter_lines():

                    if line:

                        data = line.decode("utf-8")

                        chunk = json.loads(data)


                        # Get AI text

                        if (
                            "message" in chunk
                            and "content" in chunk["message"]
                        ):

                            content = chunk["message"]["content"]

                            full_response += content


                            # Display response while generating

                            response_placeholder.markdown(
                                full_response + "▌"
                            )


                        # Stop when Ollama finishes

                        if chunk.get("done", False):

                            break


            # Display final response

            response_placeholder.markdown(
                full_response
            )


        except requests.exceptions.HTTPError as e:

            full_response = (
                f"HTTP Error: {str(e)}\n\n"
                f"The model '{model}' may not be downloaded.\n\n"
                f"Run this command in Terminal:\n\n"
                f"ollama pull {model}"
            )

            response_placeholder.error(
                full_response
            )


        except requests.exceptions.ConnectionError:

            full_response = (
                "Could not connect to Ollama.\n\n"
                "Please make sure the Ollama application "
                "is running on your Mac."
            )

            response_placeholder.error(
                full_response
            )


        except Exception as e:

            full_response = f"Error: {str(e)}"

            response_placeholder.error(
                full_response
            )


    # 5. Save AI response to memory

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )