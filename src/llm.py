import tempfile
import logging
from openai import OpenAI
from dotenv import load_dotenv
from prompt import prompt, schema
from jsonschema import validate, ValidationError
import os
import json
import asyncio

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def call_and_save_response(user_prompt,date):
    try:
        response = client.chat.completions.create(
            # model="gpt-4",
            model="gpt-3.5-turbo-0125",
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt+user_prompt
                }
            ],
            response_format={"type": "json_object"},
        )

        llm_response = response.choices[0].message.content
        llm_response=json.loads(llm_response)            
        llm_response['data']=date
        return save_response(llm_response)

    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return {'date':'date',"error":"Error in getting the response."}
    
def validate_response(llm_response):
        try:
            validate(instance=llm_response, schema=schema)
            if len(llm_response.get('names_of_crops', [])) != len(llm_response.get('crops_data', {})):
                raise ValidationError("Number of items in 'names_of_crops' does not match the number of crops in 'crops_data'")
        except ValidationError as e:
            print(">>",str(e))
            return True, str(e)
        
        response = remove_empty_crops(llm_response)
        return False, ""

def save_response(llm_response):
    validation,e=validate_response(llm_response)
    if validation==False:
        # llm_response = json.loads(llm_response)
        with open(f"latest.json", "w") as f:
            json.dump(llm_response, f, ensure_ascii=False, indent=3)   
        return False,llm_response,e
    else:
        print("Going again for inconsistent json")
        with open(f"error.json", "w") as f:
            json.dump(llm_response, f, ensure_ascii=False, indent=3)          
        return True,llm_response,e
    
def refine_response(llm_response,e):
    try:
        date=llm_response['date']
    except:
        pass
    user_prompt=f'''
    I asked you to do this: {prompt.prompt} 
    But this is the response I got: {llm_response}
    Error in your response: {e}
    Improve your response please. Provide only json format and all conditions remain same. Keep date also.
    '''
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
        )

        response = chat_completion.choices[0].message.content
        response = json.loads(response)
        response['date'] = date

        return save_response(response)

    except Exception as e:
        print("lol",e)

def remove_empty_crops(response):
    if 'crops_data' in response:
        for crop, data in list(response['crops_data'].items()):
            if not data.get('advisory'):
                response['crops_data'].pop(crop)
                if crop in response.get('names_of_crops', []):
                    response['names_of_crops'].remove(crop)
    return response