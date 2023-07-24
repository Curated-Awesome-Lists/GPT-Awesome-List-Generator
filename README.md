# Awesome List Generator

This is a Python program that automatically generates an "awesome list" for a specific
keyword as a markdown file. An "awesome list" is a list of resources related to a
specific topic. Currently, the resources include GitHub projects, Google Scholar
articles, YouTube videos, and podcasts. The awesome list is automatically generated
using GPT models; you can choose between different models to generate the list, such as
GPT 3.5 or GPT 4.

## Setup

1. Make sure you are using Python 3.10.
2. Install poetry from [here](https://python-poetry.org/docs/#installation).
3. Install dependencies using poetry:
    ```bash
    poetry install
    ```
4. Create an .env file in the root of the project and add the following environment variables:
    ```
    OPENAI_API_KEY=<your_openai_api_key>
    ```

## How to use

### Using Streamlit UI

We've provided a Streamlit interface for running this application. To use it, run the following command:

1. Activate the project's virtual environment:

    ```bash
    poetry shell
    ```

2. Run the Streamlit application using Poetry:

```bash
poetry run streamlit run streamlit_run.py
```

3. Open `http://localhost:8501`

You'll be able to provide the necessary parameters through the UI and then generate your awesome list such as the openai
key, model type, keyword and description.

### Using code directly

The main class used in this project is the `AwesomeListGenerator`. It can be initialized with the following parameters:

- `keyword`: A string representing the keyword for which the awesome list will be generated.
- `description`: A string providing a description related to the keyword.
- `model`: A string representing the OpenAI model to be used for generating the markdown (default is "
  gpt-3.5-turbo-16k").
- `data_extraction_batch_size`: An integer representing the number of data items to process in each batch (default is
  10). For example, if the batch size is 10, then the data will be fetched from the data sources in batches of 10 (like
  10 github projects at a time).
- `number_of_results`: An integer representing the number of results to fetch from each data source (default is 40). the
  number of results to fetch from each data source (default is 40). For example, fetch 40 github projects then process
  them with LLM model in batches based on data_extraction_batch_size.

After initializing the class with these parameters, you can call the `save_and_return_awesome_list` method to generate
the markdown file.

Here is an example of how to use the class:

```python
# create an instance of the AwesomeListGenerator
generator = AwesomeListGenerator(keyword="Your Keyword",
                                 description="Your Description",
                                 model="gpt-3.5-turbo-16k",
                                 data_extraction_batch_size=10,
                                 number_of_results=40)
# generate and save the markdown
markdown_content = generator.save_and_return_awesome_list()
```

The program will generate a markdown file in the `output` directory named after your keyword (e.g., `Your_Keyword.md`).
This file contains the "awesome list" generated by the program.

## Support Us

We hope you find this project useful! If it's been helpful to you, please consider giving us a ⭐ on GitHub. This not
only signifies your approval of the project, but also helps us reach more people and continue development.

Also, feel free to fork the repository and submit pull requests to contribute or open an issue. Your feedback and
contributions are always welcome!
