from awesome_list_generator import AwesomeListGenerator

if __name__ == "__main__":
    keyword = "Auto-GPT"
    description = """Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI.
    """
    markdown_generator = AwesomeListGenerator(keyword, description, model="gpt-3.5-turbo-16k",
                                              data_extraction_batch_size=10)

    _, _ = markdown_generator.save_and_return_awesome_list()
