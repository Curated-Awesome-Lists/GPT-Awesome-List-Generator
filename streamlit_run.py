from typing import Dict, Tuple

import streamlit as st
from streamlit_chat import message

from awesome_list_generator import AwesomeListGenerator
from utils import timing


class AppState:
    keys = [
        "output",
        "user_input",
        "model_name",
        "tokens",
        "input_submitted",
    ]
    default_values = [
        "",
        "",
        "",
        0.0,
        False,
    ]

    @classmethod
    def initialize(cls) -> None:
        for key, default_value in zip(cls.keys, cls.default_values):
            if key not in st.session_state:
                st.session_state[key] = default_value

    @classmethod
    def reset(cls) -> None:
        for key, default_value in zip(cls.keys, cls.default_values):
            st.session_state[key] = default_value


@timing
def generate_response(
    keyword: str, description: str, model: str
) -> Tuple[str, Dict[str, int]]:
    awesome_list_generator = AwesomeListGenerator(keyword, description, model, 10, 40)
    response, usage_info = awesome_list_generator.save_and_return_awesome_list()
    return response, usage_info


def setup_streamlit():
    # Streamlit configuration
    st.set_page_config(page_title="Awesome List Generator", page_icon=":robot_face:")

    # Markdown for the application
    st.markdown(
        "<h1 style='text-align: center;'>Awesome List Generator</h1>",
        unsafe_allow_html=True,
    )


def setup_sidebar(model_map):
    st.sidebar.title("Sidebar")
    model_name = st.sidebar.radio("Choose a model:", tuple(model_map.keys()))
    counter_placeholder = st.sidebar.empty()

    return model_name, model_map[model_name]


def setup_main_container():
    if not st.session_state["input_submitted"]:
        keyword = st.text_input("keyword:")
        description = st.text_input("Describe the keyword in 1-2 sentences:")
        submit_button_slot = st.empty()
        submit_button = submit_button_slot.button(label="Create Awesome List")

        if submit_button and keyword and description:
            submit_button_slot.empty()
            with st.spinner(
                "The awesome list is being generated, this could take some minutes "
                "to finish. Please be patient"
            ):
                awesome_list, usage_info = generate_response(
                    keyword, description, model
                )
            st.session_state.update(
                {
                    "input_submitted": True,
                    "user_input": f"generate an awesome list for {keyword}",
                    "output": awesome_list,
                    "model_name": model_name,
                    "tokens": usage_info["total_tokens"],
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
                f"Number of tokens used: {st.session_state['tokens']}; "
            )


if __name__ == "__main__":
    AppState.initialize()
    setup_streamlit()
    model_map = {"GPT-3.5": "gpt-3.5-turbo-16k", "GPT-4": "gpt-4-0314"}
    model_name, model = setup_sidebar(model_map)
    if st.sidebar.button("Clear Conversation", key="clear"):
        AppState.reset()
        st.experimental_rerun()
    setup_main_container()
