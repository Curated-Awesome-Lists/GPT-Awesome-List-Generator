from typing import Dict, Tuple

import openai
from streamlit_chat import message

import streamlit as st


def initialize_session_state() -> None:
    keys = [
        "openai_api_key",
        "output",
        "user_input",
        "messages",
        "model_name",
        "tokens",
        "cost",
        "input_submitted",
    ]

    default_values = [
        "",
        "",
        "",
        [{"role": "system", "content": "You are a helpful assistant."}],
        "",
        "",
        "",
        0.0,
        False,
        "",
    ]

    for key, default_value in zip(keys, default_values):
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_session_state() -> None:
    st.session_state.update(
        {
            "input_submitted": False,
            "output": "",
            "user_input": "",
            "messages": [{"role": "system", "content": "You are a helpful assistant."}],
            "model_name": "",
            "cost": 0.0,
            "tokens": "",
        }
    )


def generate_response(prompt: str, model: str) -> Tuple[str, Dict[str, int]]:
    """Generate a response using the OpenAI API."""
    st.session_state["messages"].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model, messages=st.session_state["messages"]
    )

    response = completion.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": response})

    usage_info = {
        "tokens": completion.usage.total_tokens,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
    }
    return response, usage_info


def check_if_openai_api_key_is_submitted() -> bool:
    """Check if the OpenAI API key is submitted."""
    if not st.session_state["openai_api_key"]:
        st.error("Please enter an OpenAI API key.")
        return False
    else:
        return True


# Streamlit configuration
st.set_page_config(page_title="AVA", page_icon=":robot_face:")

# Markdown for the application
st.markdown(
    "<h1 style='text-align: center;'>Awesome List Generator</h1>",
    unsafe_allow_html=True,
)

initialize_session_state()

model_map = {"GPT-3.5": "gpt-3.5-turbo", "GPT-4": "gpt-4"}

# Check for OpenAI API key in session state
if not st.session_state["openai_api_key"]:
    with st.form(key="api_key_form"):
        st.session_state["openai_api_key"] = st.text_input(
            "Enter OpenAI API key:", type="password"
        )
        api_key_submit = st.form_submit_button("Submit API Key")
        if api_key_submit:
            st.experimental_rerun()
else:
    # Continue with application if API key exists
    openai.api_key = st.session_state["openai_api_key"]
    st.sidebar.title("Sidebar")
    model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    counter_placeholder = st.sidebar.empty()

    model = model_map[model_name]

    if st.sidebar.button("Clear Conversation", key="clear"):
        reset_session_state()

    with st.container():
        if not st.session_state["input_submitted"]:
            with st.form(key="my_form", clear_on_submit=True):
                user_input = st.text_area("You:", key="input", height=100)
                submit_button = st.form_submit_button(label="Send")
                if submit_button and user_input:
                    output, usage_info = generate_response(user_input, model)
                    st.session_state.update(
                        {
                            "input_submitted": True,
                            "user_input": user_input,
                            "output": output,
                            "model_name": model_name,
                            "tokens": usage_info["tokens"],
                            "cost": (
                                usage_info["tokens"] * 0.002 / 1000
                                if model_name == "GPT-3.5"
                                else (
                                    usage_info["prompt_tokens"] * 0.03
                                    + usage_info["completion_tokens"] * 0.06
                                )
                                / 1000
                            ),
                        }
                    )
                    st.experimental_rerun()

        else:
            with st.container():
                key = "0"
                message(st.session_state["user_input"], is_user=True, key=key + "_user")
                message(st.session_state["output"], key=key)
                st.write(
                    f"Model used: {st.session_state['model_name']}; "
                    f"Number of tokens: {st.session_state['tokens']}; "
                    f"Cost: ${st.session_state['cost']:.5f}"
                )
