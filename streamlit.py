import openai
import streamlit as st
from streamlit_chat import message


def initialize_session_state():
    keys = [
        "openai_api_key",
        "generated",
        "past",
        "messages",
        "model_name",
        "cost",
        "total_tokens",
        "total_cost",
    ]

    default_values = [
        "",
        [],
        [],
        [{"role": "system", "content": "You are a helpful assistant."}],
        [],
        [],
        [],
        0.0,
    ]

    for key, default_value in zip(keys, default_values):
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_session_state():
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state["model_name"] = []
    st.session_state["cost"] = []
    st.session_state["total_cost"] = 0.0
    st.session_state["total_tokens"] = []


def generate_response(prompt, model):
    st.session_state["messages"].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model, messages=st.session_state["messages"]
    )
    response = completion.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": response})

    usage_info = {
        "total_tokens": completion.usage.total_tokens,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
    }
    return response, usage_info


st.set_page_config(page_title="AVA", page_icon=":robot_face:")
st.markdown(
    "<h1 style='text-align: center;'>Awesome List Generator</h1>",
    unsafe_allow_html=True,
)

initialize_session_state()

model_map = {"GPT-3.5": "gpt-3.5-turbo", "GPT-4": "gpt-4"}

if not st.session_state["openai_api_key"]:
    with st.form(key="api_key_form"):
        st.session_state["openai_api_key"] = st.text_input(
            "Enter OpenAI API key:", type="password"
        )
        api_key_submit = st.form_submit_button("Submit API Key")

    if api_key_submit:
        openai.api_key = st.session_state["openai_api_key"]
else:
    openai.api_key = st.session_state["openai_api_key"]
    st.sidebar.title("Sidebar")
    model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    counter_placeholder = st.sidebar.empty()
    counter_placeholder.write(
        f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}"
    )
    clear_button = st.sidebar.button("Clear Conversation", key="clear")

    model = model_map[model_name]

    if clear_button:
        reset_session_state()
        counter_placeholder.write(
            f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}"
        )

    response_container = st.container()
    container = st.container()

    with container:
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_area("You:", key="input", height=100)
            submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input:
            output, usage_info = generate_response(user_input, model)
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)
            st.session_state["model_name"].append(model_name)
            st.session_state["total_tokens"].append(usage_info["total_tokens"])

            if model_name == "GPT-3.5":
                cost = usage_info["total_tokens"] * 0.002 / 1000
            else:
                cost = (
                    usage_info["prompt_tokens"] * 0.03
                    + usage_info["completion_tokens"] * 0.06
                ) / 1000

            st.session_state["cost"].append(cost)
            st.session_state["total_cost"] += cost

    if st.session_state["generated"]:
        with response_container:
            for i in range(len(st.session_state["generated"])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
                message(st.session_state["generated"][i], key=str(i))
                st.write(
                    f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}"
                )
                counter_placeholder.write(
                    f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}"
                )
