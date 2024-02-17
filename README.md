# gpt-driver

This is a simple app on the GPT API. It generates survey questions based on a given topic and subcategories.

## Setup

To use the app, clone the repository using the following command:

```git clone https://github.com/albert-polak/gpt-driver```

Install required python packages

```
pip install openai 
pip install tenacity
pip install gradio
``` 

Generate OpenAI API key 

```https://platform.openai.com/api-keys```

Pase the API key in key.txt file in `./gpt-driver/`

Launch the app:

```python ./app.py```

Open the web interface on local URL provided in console.

## Usage

Pick a category in the `Category` tab.

Optionally add subcategegories in the `Survey` tab and check them in the dropdown menu.

Choose number of questions and generate the survey.

In the `Answer Questions` tab refresh the questions and answer them. When you answer the questions you can get the summary provided by GPT by clicking the `Get GPT Answer` button.