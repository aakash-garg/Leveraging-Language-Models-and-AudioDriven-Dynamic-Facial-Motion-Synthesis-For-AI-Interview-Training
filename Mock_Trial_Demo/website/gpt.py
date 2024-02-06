from flask import Flask, request
import openai
from os.path import exists
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify
import requests
# from flask_login import login_required, current_user

from . import db
import json
from .models import *
from sqlalchemy import desc
from time import sleep
from sqlalchemy import func, extract
from datetime import date
# from transformers import pipeline
from flask import abort, Flask, render_template, request


import json



# Zimmerman_History="""From now on you are "Interview Coach Allen", an expert in coaching students for software engineering job interviews, with a particular focus on data structures and algorithms. Your main objective is to guide undergraduates in understanding the interview process. Your name is Allen. If asked who you are, simply say you're Allen, the Interview Coach. Keep your language as simple and understandable as possible, as if you're speaking to someone new to the field. Use easy words and brief sentences. Here are your primary tasks:

# 1 - Your mission is to simulate an uncomplicated job interview for a software engineer position. The choice will be offered to the person you're assisting.
# 2 - Begin by greeting them and explaining why practicing for job interviews is crucial.
# 3 - Before jumping into job-specific questions, ask them to give a basic introduction about themselves. This helps to create a friendly and comfortable atmosphere for the interview. Take a very deep interest in their answer and ask just one or two questions from their introductions which may or may not be related to the software engineer position. Wait for an answer.
# 4 - After the initial questions, ask whether they're prepared to start a practice round for a software engineering role.
# 5 - Next, introduce roles such as "Front-end Developer", "Back-end Developer", "Full Stack Dveloper", "Database Manager", "System Analyst" as examples.
# 6 - All your subsequent questions should be about the software engineer role. Wait for an answer.
# 7 - Proceed with a basic question about data structures or algorithms. Once you receive an answer, commend their clarity and offer a simple suggestion to improve it. However, don't announce that you're going to do this, just proceed with it. Continue asking fundamental questions about the topic, waiting for an answer each time. Do this for at least 4 questions. Keep count of the number of questions, but don't mention that you're doing so.
# 8 - After your final question, ask if they have any queries for you. Wait for an answer.
# 9 - Then, answer their questions. Wait for an answer. and end the interview by thanking them for their time and wishing them luck. 

# Ready to start!"""


# Zimmerman_History=Zimmerman_History.replace("\n", " ")
# Zimmerman_History=Zimmerman_History.replace("\s+", " ")

# app = Flask(__name__)

#http://localhost:5000/api?user_input=hello
# @app.route('/api', methods=['GET'])
# def api():
#     # Get the user input from the query string
#     user_input = request.args.get('user_input')

#     # Call the bat_chat function to get the response
#     response = zimmerman_chat(user_input)

#     # Return the response as JSON
#     return jsonify({'response': response})

# @app.route('/chatbot_api', methods=['POST'])
# def chatbot_api():
#     message = request.form['message']
#     answer = zimmerman_chat(message)
#     response = {'answer': answer}

#     return jsonify(response)


def zimmerman_chat(user_input, user_id):
    zimmerman_memory = PastorMemory.query.filter_by(user_id=user_id).first()
    user_form = UserForm.query.filter_by(user_id=user_id).first()  # Fetch user data
    user_cv = UserCV.query.filter_by(user_id=user_id).first() 
    current_user = User.query.filter_by(id=user_id).first()
    if user_cv and user_cv.details:
        user_intro = f"I am {current_user.name}. Here are my details: {user_cv.details}"
    elif user_form:
        user_intro = f"I am {current_user.name}. I have a background in {user_form.education}. My skills include {user_form.skills} and I have experience in {user_form.experiences}."
    else:
        user_intro = None
    
    if not user_intro:
        Zimmerman_History = """From now on you are "Interview Coach Allen", an expert in coaching students for nursing job interviews. Your main objective is to guide aspiring nurses in understanding the interview process. Your name is Allen. If asked who you are, simply say you're Allen, the Interview Coach. Keep your language as simple and understandable as possible, as if you're speaking to someone new to the field. Use easy words and brief sentences. Here are your primary tasks:

    1 - Your mission is to simulate an uncomplicated job interview for a nursing position. The choice will be offered to the person you're assisting.
    2 - Begin by greeting them and explaining why practicing for job interviews is crucial in the healthcare field.
    3 - Before diving into job-specific questions, ask them to give a basic introduction about themselves. Take a keen interest in their answer and inquire about one or two points from their introduction which may or may not be related to the nursing position. Wait for an answer.
    4 - After the initial questions, inquire if they're ready to start a practice round for a nursing role.
    5 - Introduce roles such as "Registered Nurse", "Pediatric Nurse", "Oncology Nurse", "Nurse Practitioner", "Nurse Anesthetist" as examples.
    6 - All your subsequent questions should be about the nursing role. Wait for an answer.
    7 - Proceed with a basic question about patient care, procedures, or nursing protocols. Once you receive an answer, commend their clarity and offer a simple suggestion to enhance it. Continue asking fundamental questions about nursing, waiting for an answer each time. Do this for at least 4 questions.
    8 - After your final question, ask if they have any questions for you. Wait for an answer.
    9 - Then, let them know they can swap roles with you. You will now be the interviewee, and they can ask you questions.

    Ready to start! Wait for their text input and start the interview process as described above."""
    
    
    # else:
    #     Zimmerman_History = f"""From now on you are "Interview Coach Allen", an expert in coaching students for nursing job interviews. Your main objective is to guide aspiring nurses in understanding the interview process. Your name is Allen. If asked who you are, simply say you're Allen, the Interview Coach. Keep your language as simple and understandable as possible. Here are your primary tasks:

    # 1 - Your mission is to engage with the candidate, fostering an understanding of their background and potential fit for nursing roles.
    # 2 - Begin by greeting them and explaining the importance of understanding their own background and skills in nursing job interviews. Then ask if they are ready to start. Wait for an answer.
    # 3 - You've already received their introduction and background from the candidate: '{user_intro}'. Now, delve deeper into their background. Ask 1 specific question related to their education, clinical experiences, and certifications, as these are pertinent to nursing. Show genuine interest in the details they've provided. Wait for an answer.
    # 4 - Now ask 1 more question from their introduction information, wait for an answer.
    # 5 - Now ask 1 more question from their introduction information, wait for an answer.
    # 6 - Now ask 1 more question from their introduction information, wait for an answer.
    # 7 - After understanding their background, ask them about the nursing specialties they are interested in.
    # 8 - Based on their responses and background, provide feedback and potential suggestions, like "Pediatric Nursing", "Critical Care", "Mental Health Nursing", etc. Wait for their response.
    # 9 - Conclude by asking if they have any questions for you. Wait for an answer.
    # 10 - Answer their questions and end the conversation by thanking them for their time and wishing them success in their nursing journey.

    # Ready to start! Wait for their text input and begin the interview process as detailed above."""
    else:
        Zimmerman_History =   f"""From now on you are prosecutor Allen in a mock court setting, designed to train forensic nurses who specialize in sexual assault cases. Your main objective is to simulate a realistic cross-examination process, focusing on the nurse's professional qualifications, their handling of evidence, and their patient care protocols.  Keep your language as simple and understandable as possible. You will only respond in one or two lines and ask one question. Here are your primary tasks:
    1 - Your mission is not to intimidate but to prepare the nurse for the types of questions and scenarios they may face in a real court setting.
    2 - Begin by greeting them and explaining the importance of understanding their own background and skills in forensic nursing. Then ask if they are ready to start. Wait for an answer.
    3 - You've already received their introduction and background from the candidate: '{user_intro}'. Now, delve deeper into their background. Ask 1 specific question related to their education, clinical experiences, and certifications, as these are pertinent to nursing. Show genuine interest in the details they've provided. Wait for an answer.
    4 - Now ask 1 more question from their introduction information, wait for an answer.
    5 - Now ask 1 more question on their knowledge and application of protocols for evidence collection in sexual assault cases, wait for an answer.
    6 - Follow up with another question on the same topic.
    7 - Explore the nurse's approach to patient care, emphasizing empathy, communication skills, and the ability to provide a safe and supportive environment for sexual assault survivors, Ask 1 more question on how they navigate consent for examination and evidence collection, ensuring the patient's rights and choices are respected.
    8 - Now ask i more question that will delve into the nurse's experience working with law enforcement, legal teams, and other healthcare professionals. Focus on how they communicate findings and collaborate on cases, Inquire about their testimony experience, if any, and how they prepare for court appearances to ensure their findings are accurately represented.

   Ready to start! Wait for their text input and begin the mock trial process process as detailed above. Your questions should encourage thoughtful responses, demonstrate the nurse's competency and professionalism, and highlight the critical role of forensic nursing in the justice system."""



    if not zimmerman_memory:
        zimmerman_memory = PastorMemory(
            user_id=user_id,
            counter_zimmerman=-1,
            counter_zimmerman_new=-1,
            prompt_zimmerman_new='-1',
            prompt_zimmerman_second='-1'
        )
        db.session.add(zimmerman_memory)
        db.session.commit()

    if user_input=="<reset>":
        zimmerman_memory.counter_zimmerman = -1
        zimmerman_memory.counter_zimmerman_new = -1
        zimmerman_memory.prompt_zimmerman_new = '-1'
        zimmerman_memory.prompt_zimmerman_second = '-1'
        db.session.commit()
        return "Reset Done, Memory cleared"

    
    openai.api_key = "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"
    


    prompt_orig_new = [
        {"role": "system", "content":Zimmerman_History}
    ]



    k = zimmerman_memory.counter_zimmerman if zimmerman_memory.counter_zimmerman != -1 else 0
    k_new = zimmerman_memory.counter_zimmerman_new if zimmerman_memory.counter_zimmerman_new != -1 else 0
    prompt_orig = json.loads(zimmerman_memory.prompt_zimmerman_new) if zimmerman_memory.prompt_zimmerman_new != '-1' else []


    K_MAX=3
    K_NEW_MAX=4


    query=user_input
    
    prompt_orig.append({"role": "user", "content": query})
    prompt=prompt_orig

    if query=="bye":
        return "Thanks for visiting"

    # model_engine = "gpt-3.5-turbo-16k-0613"
    model_engine = "gpt-4-0613" 
    max_tokens = 25
    temperature = 0.7
    prompt_to_generate = prompt_orig_new
    prompt_to_generate.extend(prompt)
    # print(prompt_to_generate)
    # Generate response using OpenAI
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=prompt_to_generate
        )

    # Extract and return the response text
    results = response['choices'][0]['message']['content']
    # return response_text

    final_output=results


    if k<K_MAX:
        # prompt=prompt+final_output+"\""
        prompt.append( {"role": "assistant", "content": final_output})
        k=k+1
        zimmerman_memory.prompt_zimmerman_new = json.dumps(prompt)
        prompt_orig=prompt
        zimmerman_memory.counter_zimmerman = k

    if k>=K_MAX and k_new<K_NEW_MAX:
        if zimmerman_memory.prompt_zimmerman_second == '-1':
            k_new=k_new+1
            # prompt_orig.append( {"role": "assistant", "content": final_output})
            zimmerman_memory.counter_zimmerman_new = k_new
            zimmerman_memory.prompt_zimmerman_second = json.dumps(prompt_orig)

        else:
            k_new=k_new+1

            prompt_orig.append({"role": "assistant", "content": final_output})
            zimmerman_memory.prompt_zimmerman_new = json.dumps(prompt_orig)
            zimmerman_memory.counter_zimmerman_new = k_new
    elif k_new>=K_NEW_MAX and k>=K_MAX:
        prompt_orig = json.loads(zimmerman_memory.prompt_zimmerman_second)
        prompt_orig.append({"role": "user", "content": query})
        prompt_orig.append({"role": "assistant", "content": final_output})
        zimmerman_memory.prompt_zimmerman_new = json.dumps(prompt_orig)
        k_new = 1
        zimmerman_memory.counter_zimmerman_new = k_new

    db.session.commit()
    return final_output


# if __name__ == '__main__':
#     app.run()
