import streamlit as st

from awesome_list_generator import AwesomeListGenerator
from utils import timing


class AppState:
    keys = [
        "output",
        "user_input",
        "model_name",
        "tokens",
        "input_submitted",
        "awesome_list",
        "usage_info",
    ]
    default_values = ["", "", "", 0.0, False, "", {}]

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
) -> tuple[str, dict[str, float]]:
    awesome_list_generator = AwesomeListGenerator(keyword, description, model, 10, 40)
    response, usage_info = awesome_list_generator.save_and_return_awesome_list()
    return response, usage_info


def setup_streamlit():
    st.set_page_config(page_title="Awesome List Generator", page_icon=":robot_face:")
    st.markdown(
        "<h1 style='text-align: center; font-size:3em;'>Awesome List Generator</h1>",
        unsafe_allow_html=True,
    )


def setup_sidebar(model_map):
    st.sidebar.title("Sidebar")
    model_name = st.sidebar.radio("Choose a model:", tuple(model_map.keys()))
    counter_placeholder = st.sidebar.empty()
    return model_name, model_map[model_name]


def setup_main_container():
    st.markdown(
        """
        This tool generates an awesome list based on your input parameters. It includes resources like GitHub projects, 
        Google Scholar articles, YouTube videos, and podcasts. The awesome list is automatically generated using GPT models.
    """
    )

    keyword = st.text_input(
        "Keyword",
        help="The keyword is critical for good results because we use it to search for repos in GitHub or videos on YouTube, etc.",
    )
    description = st.text_area(
        "Description",
        help="This description is used to filter the results with the LLM to ensure we have relevant results. It is also the description we show in the final markdown.",
    )
    if st.session_state["awesome_list"]:
        awesome_list = st.session_state["awesome_list"]
        usage_info = st.session_state["usage_info"]

        st.markdown("Your Awesome List is Ready!")
        st.markdown("---")
        st.markdown(awesome_list, unsafe_allow_html=True)
        st.markdown(
            f"Model used: {model_name}; Number of tokens used: {usage_info['total_tokens']};"
        )
        st.download_button(
            "Download Awesome List",
            data=awesome_list,
            file_name=f"{model_name}_Awesome_List.md",
            mime="text/markdown",
        )

    elif keyword and description:
        create_button = st.empty()
        if create_button.button("Create Awesome List"):
            create_button.empty()
            with st.spinner(
                "The awesome list is being generated. This could take some minutes to finish. Please be patient."
            ):
                awesome_list, usage_info = generate_response(
                    keyword, description, model
                )
            st.session_state["awesome_list"] = awesome_list
            st.session_state["usage_info"] = usage_info
            st.experimental_rerun()


if __name__ == "__main__":
    AppState.initialize()
    setup_streamlit()
    model_map = {"GPT-3.5": "gpt-3.5-turbo-16k", "GPT-4": "gpt-4-0314"}
    model_name, model = setup_sidebar(model_map)
    if st.sidebar.button("Clear Conversation", key="clear"):
        AppState.reset()
        st.experimental_rerun()
    setup_main_container()
