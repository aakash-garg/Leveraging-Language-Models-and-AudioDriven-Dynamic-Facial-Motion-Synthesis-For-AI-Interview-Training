from flask import Flask, request
import openai
from os.path import exists
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify
import requests
# from flask_login import login_required, current_user

# from . import db
import json

from sqlalchemy import desc
from time import sleep
from sqlalchemy import func, extract
from datetime import date
# from transformers import pipeline
from flask import abort, Flask, render_template, request


import json





def summarize_pdf_old(user_input):


    Zimmerman_History = f"""
    Please review the provided nursing CV document and summarize it into its key sections, ensuring that the summary does not exceed 500 words. If the following areas are present, make sure to highlight them separately. In your summary, refer to the individual whose CV it is as 'user' instead of using their actual name.

    1. Education: Detail the institutions 'the user' attended, nursing degrees earned, areas of study, and years of graduation. Highlight any specialized nursing courses, training, or certifications, such as Critical Care, Pediatrics, or Oncology.

    2. Clinical Skills: List the nursing procedures and techniques 'the user' is proficient in. This may include things like wound care, patient assessment, administering medication, and any other specialized skills related to nursing.

    3. Experience: Extract 'the user's' nursing history, including job titles (e.g., Registered Nurse, Nurse Practitioner), healthcare facilities or hospitals worked for, duration of employment, patient demographics served (e.g., pediatric, geriatric), and primary responsibilities and achievements in each role.

    4. Clinical Rotations or Internships: If 'the user' is a recent graduate, outline any clinical rotations, including the department (e.g., ER, ICU, Pediatrics), responsibilities, and any commendations received.

    5. Other Relevant Information: Include any additional pertinent information such as 'the user's' certifications (e.g., BLS, ACLS, PALS), publications related to nursing, awards, languages known (especially if relevant for patient care), volunteering experience in healthcare settings, and any affiliations with nursing associations or organizations.

    The aim is to provide a concise but comprehensive summary of the CV's key points, focusing on the individual's capabilities and contributions to the nursing field. Remember, the total length of your summary should not exceed 500 words. Refer to the individual only as 'user' in the summary and avoid including any personal identifiers.
    """

    
    openai.api_key = "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"
    


    prompt_orig_new = [
        {"role": "system", "content":Zimmerman_History}
    ]


    prompt_orig = []
    query=user_input
    
    prompt_orig.append({"role": "user", "content": query})
    prompt=prompt_orig


    model_engine = "gpt-3.5-turbo-1106" 
    max_tokens = 25
    temperature = 0.7
    prompt_to_generate = prompt_orig_new
    prompt_to_generate.extend(prompt)
    # print(prompt_to_generate)
    # Generate response using OpenAI
    print ("Generating summary...")
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=prompt_to_generate
        )

    # Extract and return the response text
    results = response['choices'][0]['message']['content']
    # return response_text

    final_output=results
    # print (final_output)
    return final_output



def summarize_pdf(user_input):
    General_Prompt = f"""
    Please review the provided nursing CV document and summarize it into its key sections, ensuring that the summary does not exceed 500 words. If the following areas are present, make sure to highlight them separately. In your summary, refer to the individual whose CV it is as 'user' instead of using their actual name.

    1. Education: Detail the institutions 'the user' attended, nursing degrees earned, areas of study, and years of graduation. Highlight any specialized nursing courses, training, or certifications, such as Critical Care, Pediatrics, or Oncology.

    2. Clinical Skills: List the nursing procedures and techniques 'the user' is proficient in. This may include things like wound care, patient assessment, administering medication, and any other specialized skills related to nursing.

    3. Experience: Extract 'the user's' nursing history, including job titles (e.g., Registered Nurse, Nurse Practitioner), healthcare facilities or hospitals worked for, duration of employment, patient demographics served (e.g., pediatric, geriatric), and primary responsibilities and achievements in each role.

    4. Clinical Rotations or Internships: If 'the user' is a recent graduate, outline any clinical rotations, including the department (e.g., ER, ICU, Pediatrics), responsibilities, and any commendations received.

    5. Other Relevant Information: Include any additional pertinent information such as 'the user's' certifications (e.g., BLS, ACLS, PALS), publications related to nursing, awards, languages known (especially if relevant for patient care), volunteering experience in healthcare settings, and any affiliations with nursing associations or organizations.

    The aim is to provide a concise but comprehensive summary of the CV's key points, focusing on the individual's capabilities and contributions to the nursing field. Remember, the total length of your summary should not exceed 500 words. Refer to the individual only as 'user' in the summary and avoid including any personal identifiers.
    """

    CV_Prompt = General_Prompt

    openai.api_key = "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"

    model_engine = "gpt-3.5-turbo-1106" 
    max_tokens = 25
    temperature = 0.7

    def generate_summary(query, is_general_prompt=False):
        if is_general_prompt:
            prompt_text = General_Prompt
        else:
            prompt_text = CV_Prompt
        
        prompt_orig_new = [{"role": "system", "content": prompt_text}]
        prompt_orig = [{"role": "user", "content": query}]
        prompt_to_generate = prompt_orig_new
        prompt_to_generate.extend(prompt_orig)

        print ("Generating summary...")
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=prompt_to_generate
        )

        # Extract and return the response text
        return response['choices'][0]['message']['content']
    thres=50000
    # Divide the text into parts of thres characters each
    input_parts = [user_input[i:i+thres] for i in range(0, len(user_input), thres)]

    # Summarize each part with CV prompt
    summarized_parts = []

    for part in input_parts:
        # print (part)
        try:
            summarized_parts.append(generate_summary(part))
        except Exception as e:
            print(f"An error occurred during summarization: {e}")
            # summarized_parts.append(part)
    # summarized_parts = [generate_summary(part) for part in input_parts]

    # Join the summarized parts
    full_summary = ' '.join(summarized_parts)

    if len(full_summary)>thres:
        full_summary=full_summary[:thres]

    # while len(full_summary) > thres:
    #     input_parts = [full_summary[i:i+thres] for i in range(0, len(full_summary), thres)]
    #     summarized_parts = [generate_summary(part) for part in input_parts]
    #     full_summary = ' '.join(summarized_parts)

    # Summarize the entire thing with general prompt to get the final result
    final_output = generate_summary(full_summary, is_general_prompt=True)
    print (final_output)
    return final_output
