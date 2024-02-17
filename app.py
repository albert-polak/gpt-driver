import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json
import gradio as gr

GPT_MODEL = "gpt-3.5-turbo"

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

openai.api_key = open('./key.txt', 'r').read().strip('\n')

client = openai.OpenAI(api_key=open('./key.txt', 'r').read().strip('\n'))

messages = []
subcategories = []
questions = None

question_index = 0

import gradio as gr

def change_category(category):
    return category

def add_subcategory(subcategory):
    global subcategories
    if subcategory not in subcategories and subcategory != "":
        subcategories.append(subcategory)
    # print(subcategories)
    return gr.Dropdown(choices=subcategories, interactive=True, multiselect=True, label="Subcategory")

def refresh_question_interface():
    global questions
    global messages
    global question_index
    if messages:
        messages = [messages[0]]
        # print(messages[0])
    question_index = 0
    # print(questions)
    if questions!=None and len(questions)>0:
        question = gr.Textbox(lines=1, label="Question", interactive=False, value=questions[question_index])
        
        messages.append({"role": "assistant", "content": questions[question_index]})

        return question
    else:
        question_output = gr.Textbox(lines=1, label="Output", interactive=False, value="No questions available")
        return question_output

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
        question_slider = gr.Slider(1, 20, value=1, step=1, label="Number of questions", info="Choose between 2 and 20")

        output = gr.Textbox(lines=10, label="Output")
        submit_button = gr.Button("Submit")
        # send a request to openai
        def submit_question(category, dropdown, slider):
            global messages
            if category == "" or category.strip() == "":
                return "Please choose a category"
            
            global questions
            messages = []
            if dropdown is None:
                messages.append({"role": "system", "content": f"You are an expert in {category}."})
            else:    
                messages.append({"role": "system", "content": f"You are an expert in {category}. You specialize in {dropdown}."})
            messages.append({"role": "user", "content": f"Write {slider} different survey questions in your area of expertise."})
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
            
        submit_button.click(submit_question, inputs=[category_chosen, dropdown_sub, question_slider], outputs=[output])
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
            
        def answer(answer, question_interface):
            global question_index
            
            if question_interface == "No questions available":
                return "No questions available"
            if answer == "" or answer.strip() == "":
                return questions[question_index]
            else:
                messages.append({"role": "user", "content": answer})
                question_index += 1
                while question_index < len(questions) and questions[question_index] == '':
                    question_index += 1
                if question_index < len(questions):
                    messages.append({"role": "assistant", "content": questions[question_index]})
                    return questions[question_index]
                
                else:
                    return "No more questions available"
        answer_button.click(answer, inputs=[answer_input, question_interface], outputs=[question_interface])

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

    