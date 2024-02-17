import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json
import gradio as gr

GPT_MODEL = "gpt-3.5-turbo"

# Function from OpenAI API documentation to send a request to the API
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

# Set the API key from the key.txt file
openai.api_key = open('./key.txt', 'r').read().strip('\n')

# Create the OpenAI client with the API key
client = openai.OpenAI(api_key=open('./key.txt', 'r').read().strip('\n'))

# Initialize global variables to store the messages questions and subcategories
messages = []
subcategories = []
questions = None

# Initialize the question index for survey answering
question_index = 0

# Import gradio for the web interface
import gradio as gr

# Function to change the category
def change_category(category):
    return category

# Function to add a subcategory
def add_subcategory(subcategory):
    global subcategories
    if subcategory not in subcategories and subcategory != "":
        subcategories.append(subcategory)
    # print(subcategories)
    return gr.Dropdown(choices=subcategories, interactive=True, multiselect=True, label="Subcategory")

# Function to refresh the question list
def refresh_question_interface():
    global questions
    global messages
    global question_index

    # Add the system message to the message history for chat gpt
    if messages:
        messages = [messages[0]]
        # print(messages[0])

    # Reset the question index each time the questions are refreshed
    question_index = 0
    # print(questions)
    if questions!=None and len(questions)>0:
        question = gr.Textbox(lines=1, label="Question", interactive=False, value=questions[question_index])
        
        # add the first question to the message history
        messages.append({"role": "assistant", "content": questions[question_index]})

        return question
    else:
        question_output = gr.Textbox(lines=1, label="Output", interactive=False, value="No questions available")
        return question_output

# Create the web interface
with gr.Blocks() as demo:    
    with gr.Tab("Category"):
        category = gr.Textbox(lines=1, label="Category")
        category_chosen = gr.Textbox(lines=1, label="Chosen Category")
        category_button = gr.Button("Choose Category")
        category_button.click(change_category, inputs=[category], outputs=[category_chosen])
            
        
    with gr.Tab("Survey"):
        subcategory = gr.Textbox(lines=1, label="Subcategory")
        subcategory_button = gr.Button("Add Subcategory")

        dropdown_sub = gr.Dropdown(subcategories, label="Subcategory", choices=subcategories)
        
        subcategory_button.click(add_subcategory, inputs=[subcategory], outputs=[dropdown_sub])
        question_slider = gr.Slider(1, 10, value=1, step=1, label="Number of questions", info="Choose between 1 and 10")

        output = gr.Textbox(lines=10, label="Output")
        submit_button = gr.Button("Submit")
        
        # Function to request the survey questions from the GPT model
        def get_questions(category, dropdown, slider):
            global messages
            global questions

            # prevent the user from getting the survey without choosing a category
            if category == "" or category.strip() == "":
                return "Please choose a category"
            
            # reset the message history for the chat gpt
            messages = []

            # add the system message and user query to get the expected behavior from the GPT model
            if dropdown is None:
                messages.append({"role": "system", "content": f"You are an expert in {category}."})
            else:    
                messages.append({"role": "system", "content": f"You are an expert in {category}. You specialize in {dropdown}."})
            messages.append({"role": "user", "content": f"Write {slider} different survey questions in your area of expertise."})
            
            # get the survey questions from the GPT model
            chat_response = chat_completion_request(
                messages
            )
            assistant_message = chat_response.choices[0].message
            messages.append({"role": "assistant", "content": assistant_message})

            # print(f"You are an {category} expert. You specialize in {', '.join(dropdown)}.")
            # print(messages)

            questions = assistant_message.content.splitlines()
            return assistant_message.content
        
            # questions = ["What is the best way to do X?", "", "", "What is the best way to do Y?"]
            # return questions
            
        submit_button.click(get_questions, inputs=[category_chosen, dropdown_sub, question_slider], outputs=[output])
    
    with gr.Tab("Answer Questions"):
        with gr.Row():
            with gr.Column():
                refresh_button = gr.Button("Refresh")
                question_interface = gr.Textbox(lines=1, label="Question", value="No questions available", interactive=False)
                refresh_button.click(refresh_question_interface, inputs=[], outputs=[question_interface])

                answer_input = gr.Textbox(lines=10, label="Answer", interactive=True, placeholder="Type your answer here.")
                answer_button = gr.Button("Answer")
            
            with gr.Column():
                gpt_output = gr.Textbox(lines=10, label="GPT Output", interactive=False, placeholder="Here the GPT output will be displayed.")
                gpt_answer_button = gr.Button("Get GPT Answer")
            
        # Function to submit answers the survey questions
        def answer(answer, question_interface):
            global question_index
            
            # prevent the user from answering the survey without refreshing the questions
            if question_interface == "No questions available":
                return "No questions available"
            # prevent the user from submitting an empty answer
            if answer == "" or answer.strip() == "":
                return questions[question_index]
            else:
                # add the user answer to the message history for the chat gpt
                messages.append({"role": "user", "content": answer})
                question_index += 1

                # skip empty questions
                while question_index < len(questions) and questions[question_index] == '':
                    question_index += 1

                # add the next question to the message history for the chat gpt
                if question_index < len(questions):
                    messages.append({"role": "assistant", "content": questions[question_index]})
                    return questions[question_index]
                
                else:
                    return "No more questions available"
        answer_button.click(answer, inputs=[answer_input, question_interface], outputs=[question_interface])

        # Function to get the GPT summary for the survey answers
        def get_gpt_answer(question_interface):
            if question_interface == "No questions available" or len(messages) <= 3:
                return "Please refresh the questions and answer them first"

            messages.append({"role": "user", "content": 'Analyze my previous answers and results of this survey.'})
            chat_response = chat_completion_request(
                messages
            )
            assistant_message = chat_response.choices[0].message

            messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message.content
            # return messages
        gpt_answer_button.click(get_gpt_answer, inputs=[question_interface], outputs=[gpt_output])




demo.launch()

    