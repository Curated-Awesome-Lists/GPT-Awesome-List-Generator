# Awesome List Generator 📜✨ [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

This is a Python program that automatically generates an "awesome list" for a specific
keyword as a markdown file. An "awesome list" is a list of resources related to a
specific topic. Currently, the resources include GitHub projects, Google Scholar
articles, YouTube videos, courses, slides and presentations, software and tools and podcasts. The awesome list is automatically generated
using GPT models; you can choose between different models to generate the list, such as
GPT 3.5 or GPT 4.

## Demo 🎥


https://github.com/alialsaeedi19/GPT-Awesome-List-Generator/assets/21360696/0029cb67-0ba1-459f-bb1d-0bd73b7c6df5


## Setup ⚙️

1. Make sure you are using Python 3.10.
2. Install poetry from the [official site](https://python-poetry.org/docs/#installation).
3. Install dependencies using poetry:
    ```bash
    poetry install
    ```
4. Create an .env file at the root of the project and add the following environment variable:
    ```
    OPENAI_API_KEY=<your_openai_api_key>
    ```
   
### Setting up Google Cloud API Key and Custom Search Engine ID

####  Prerequisites
A Google account.

#### Instructions
1. Obtain a Google Cloud API Key

- Visit the [Google Cloud Console](https://console.cloud.google.com/).

- If you haven't already, create a new project by clicking on the "Select a project" dropdown at the top-right corner, then click on "NEW PROJECT".

- Once your project is created and selected, navigate to the Navigation menu (three horizontal lines at the top-left corner), and then click on "APIs & Services" > "Credentials".

- Click on the "Create Credentials" button and select "API key". Once created, your API key will be displayed.

- Copy your API key and save it securely. You'll use this key in your application to authenticate your requests.


2. Set Up a Custom Search Engine and Get the Search Engine ID

 - Go to [Google Custom Search homepage](https://cse.google.com/cse/).

 - Click on "Create a custom search engine".

 - In the "Sites to search" section, you can specify websites you want to search or choose "Search the entire web" to allow broader search capabilities. However, if you choose "Search the entire web", make sure to toggle "Search only included sites" off under the "Sites to search" section.

 - Fill in other required fields like the name of your search engine.

 - Click on the "Create" button at the bottom.

 - Once your search engine is created, you'll be directed to a setup page. Here, find and copy the "Search engine ID" (also called "cx" in some contexts). You'll use this ID in your application to specify which custom search engine to use for queries.

3. Enable the Custom Search API for Your Project:

- Visit the [Google Cloud Console](https://console.cloud.google.com/).
- Navigate to "APIs & Services" > "Library".
- Search for "Custom Search API".
- Click on it, and you should see an "Enable" button. Click that button to enable the Custom Search API for your project.

Finally, add the following environment variables to .env file:

```
    GOOGLE_CLOUD_API_KEY='<google cloud api key>'
    CUSTOM_SEARCH_ENGINE_ID='<custom search engine id>'
```


## Usage 💻

### Using Streamlit UI

We've provided a Streamlit interface for running this application. To use it:

1. Run the Streamlit application using Poetry:
    ```bash
    poetry run streamlit run streamlit_run.py
    ```

2. Open `http://localhost:8501`

You can easily input the necessary parameters (like model type, keyword, and description) through the UI and generate
your awesome list!

### Direct Code Usage

The main class used in this project is the `AwesomeListGenerator`. This class accepts the following parameters:

- `keyword`: A string representing the keyword for which the awesome list will be generated.
- `description`: A string providing a description related to the keyword.
- `model`: A string representing the OpenAI model to be used for generating the markdown (default is "
  gpt-3.5-turbo-16k").
- `data_extraction_batch_size`: An integer representing the number of data items to process in each batch (default is
  10). For example, if the batch size is 10, then the data will be fetched from the data sources in batches of 10 (like
  10 github projects at a time).
- `number_of_results`: An integer representing the number of results to fetch from each data source (default is 20). the
  number of results to fetch from each data source (default is 20). For example, fetch 20 Github projects then process
  them with LLM model in batches based on data_extraction_batch_size.

After initializing the class with these parameters, invoke the `save_and_return_awesome_list` method to generate the
markdown file. Here's an example:

```python
# Initialize an instance of the AwesomeListGenerator
generator = AwesomeListGenerator(keyword="Your Keyword",
                                 description="Your Description",
                                 model="gpt-3.5-turbo-16k",
                                 data_extraction_batch_size=10,
                                 number_of_results=20)
# Generate and save the markdown
markdown_content = generator.save_and_return_awesome_list()
```

The program will generate a markdown file in the `output` directory named after your keyword (e.g., `Your_Keyword.md`).
This file contains the "awesome list" generated by the program.

## How It Works 🕹️

The `AwesomeListGenerator` program operates in two main phases: Data Scraping and Data Processing.

### Data Scraping 🕸️

In the data scraping phase, the program fetches resources related to your provided keyword from multiple data sources.
Currently, the resources include GitHub repositories, Google Scholar articles, YouTube videos, and podcasts. The program
utilizes specialized scrapers for each source, each of which is designed to fetch the most relevant and highest quality
resources.

For instance, the GitHub scraper fetches repositories that match the keyword, sorted by the number of stars (a common
indicator of a repository's relevance and quality). Similarly, the Google Scholar scraper retrieves articles related to
the keyword and sorted by citation count.

### Data Processing 🧠

Once the data is scraped, it is passed on to the data processing phase. In this phase, the program uses the selected GPT
model to process the fetched resources. The model filters and ranks the resources based on relevance to the keyword,
quality of content, and potential usefulness to users. The GPT model also formats the data into a markdown list, adding
necessary formatting such as links and brief descriptions.

Notably, both scraping and processing operations are executed in batches. This batch-wise operation allows the program
to support as many results as needed, based on the configured `number_of_results` and `data_extraction_batch_size`. This
way, you have control over the extent of data being handled at a time, ensuring efficient resource usage.

## Expansion and Contributions 💡

We're looking to expand the number of data sources in the future. Here are some ideas we have in mind:

- Scrape resources from Medium.
- Search for related books using Google Books or Amazon API.
- Fetch blog posts from dev.to and other developer-focused platforms.
- Retrieve documents from preprint servers like arXiv and bioRxiv.
- Extract relevant resources from online course platforms such as Coursera, Udemy, and Khan Academy.

If you're interested in contributing, you can pick one of the above tasks or propose your own ideas. We welcome all
kinds of contributions and appreciate your interest in our project!

## TODO Checklist

- [x] Add section for articles
- [x] Add section for courses
- [x] Add section for books
- [x] Add section for research papers
- [x] Add section for podcasts
- [x] Add section for slides and presentations
- [x] Add section for software and tools
- [x] Add section for videos
- [x] Add section for conferences and events
- [x] Support github collections and topics
- [ ] **Additional Use Cases**
    - [ ] Not only create 'Awesome Lists'
    - [ ] Track daily, weekly, and monthly updates on a specific topic
- [ ] **Website Enhancement**
    - [ ] User-friendly and easy navigation
    - [ ] Real-time collaboration feature
    - [ ] Exporting options in different formats
    - [ ] Interactive resource visualization
    - [ ] Advanced filters, tags, and sorting options
- [ ] **GPT Model Options**
    - [ ] Support for more GPT model options to better match user research needs
- [ ] **Notification Feature**
    - [ ] Alert users about new resources and updates in their areas of interest
- [ ] **Community Contribution Platform**
    - [ ] Allow community members to add, check, and rank resources
- [ ] **API Integration**
    - [ ] Allow other developers to build on this tool



## Projects Created Using Our Tool 🚀

- [Awesome Auto-GPT](https://github.com/alronz/Awesome-Auto-GPT) - This awesome list is dedicated to Auto-GPT, a pioneering open-source project that showcases the capabilities of the GPT-4 language model. Auto-GPT is at the forefront of AI, seamlessly chaining together Large Language Model (LLM) "thoughts" to autonomously accomplish any set objectives, thereby redefining the boundaries of what AI can do.
- [Awesome Automatic1111 (a1111) Stable Diffusion WebUI](https://github.com/alronz/awesome-stable-diffusion-webui) - An awesome list centering on the Automatic1111 (a1111) Stable Diffusion WebUI, an interactive browser interface for the Stable Diffusion generative model. This tool simplifies the process of creating realistic images from textual or visual inputs, and its user-friendly interface, built on Gradio, makes web-based interaction with machine learning models more accessible.
- [Awesome AI Talking Heads](https://github.com/alronz/awesome-ai-talking-heads) - This awesome list focuses on the fascinating domain of 'Talking Head Generation', which involves creating lifelike digital representations of human heads and faces. The list includes a collection of key research papers, state-of-the-art algorithms, important GitHub repositories, educational videos, insightful blogs, and more. It serves as a one-stop resource for AI researchers, computer graphics professionals, or AI enthusiasts looking to delve into the world of Talking Head Generation.


We love seeing the incredible awesome lists that our community creates. If you've used our tool to generate an awesome list, feel free to [let us know](https://github.com/alialsaeedi19/GPT-Awesome-List-Maker/issues/new), and we will feature your project here!


## Support Us ❤️

Did you find this project useful? If it has brought value to you, please give us a ⭐ on GitHub. This gesture not only
validates our efforts but also helps this project reach more people and continue development.

Feel free to fork the repository, contribute by submitting pull requests, or open an issue. Your feedback and
contributions are always welcome!
