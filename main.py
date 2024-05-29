import time
import tempfile
from utils.scraper import scraper, move_json_to_history, download_pdf
from utils.ocr import get_hindi_text
from utils.translate import translate_text_bhashini
import logging
from openai import OpenAI
from dotenv import load_dotenv
from prompt import prompt
from jsonschema import validate, ValidationError
import os
import json

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def call_and_save_response(user_prompt):
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
        
        return save_response(llm_response)

    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return {'date':'date',"error":"Error in getting the response."}
    
def validate_response(llm_response):
        try:
            validate(instance=llm_response, schema=prompt.schema)
            if len(llm_response.get('names_of_crops', [])) != len(llm_response.get('crops_data', {})):
                raise ValidationError("Number of items in 'names_of_crops' does not match the number of crops in 'crops_data'")
        except ValidationError as e:
            return True, e
        
        response = remove_empty_crops(response)  
        return False, ""

def save_response(llm_response):
    validation,e=validate_response(llm_response)
    if validation==False:
        with open(f"latest.json", "w") as f:
            json.dump(validation[1], f, ensure_ascii=False, indent=3)   
        return False,llm_response,e
    else:
        print("Going again for inconsistent json")
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
        
 

def main():
    temp_dir = tempfile.mkdtemp()

    try:
        weather_data = scraper()
    except Exception as e:
        logging.error(f"Error getting districts data: {e}")
        print("Error scraping website")

    # move latest to history. 
    try:
        move_json_to_history()
    except Exception as e:
        print("Error moving latest to history",e)

    print("f0")
    pdf_file = download_pdf(weather_data.get('download_url'), temp_dir)
    hindi_text = get_hindi_text(pdf_file)
    english_text = translate_text_bhashini(hindi_text)
    is_inconsistent, e = call_and_save_response(english_text)

    retry=1
    
    # Iterating again on inconsistent districts
    while retry<=3 and not is_inconsistent:
        refine_response()
    #     new_data=[district_data for district_data in districts_data if district_data["district_name"] in inconsistent_districts]
    #     fallback_tasks = [process_pdf(district_data, temp_dir) for district_data in new_data]
    #     results = await asyncio.gather(*fallback_tasks)
    #     inconsistent_districts=await save_response(results,districts_data,temp_dir)
    #     retry+=1
    
    # counter=len(inconsistent_districts)
    # total_districts = len(districts_data)

    # # Sending update through webhook
    # try:
    #     webhook_url="https://discord.com/api/webhooks/1229418219316445278/Dkj1rrqHZsQ39SoMagqd2xNV4W4HwBA-xnrk6QqAnOrBV0qQ36KpMLf06EPSAgGAZdVf"
    #     data={
    #         "disctricts_done":f"{total_districts-counter}",
    #         "inconsistent_districts":str(counter),
    #         "inconsistent_districts_name":inconsistent_districts,
    #         "time":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #     }
    #     formatted_string = json.dumps(data, indent=4)
    #     payload={
    #         "content":str(formatted_string)
    #     }
    #     response = requests.post(webhook_url, json=payload)
    #     response.raise_for_status()
    #     print("Webhook notification sent successfully.")
    # except requests.exceptions.RequestException as e:
    #     print("Error sending webhook notification:", e)        

    # #Saving metadata    
    # metadata = f"District_done: {total_districts - counter}, Total_district: {total_districts}"
    # with open("meta_data.txt", "w") as meta_file:
    #     json.dump(metadata, meta_file, indent=4)


    # # Removing temp dir
    # try:
    #     shutil.rmtree(temp_dir)
    # except Exception as e:
    #     logging.error(f"Error removing temporary directory: {e}")
    

    # return "SUCCESS"


retries = 3
retry_delay = 5

for attempt in range(1, retries + 1):
    try:
        main()    
        break  # If successful, break out of the retry loop
    except Exception as e:
        logging.error(f"Attempt {attempt}: An error occurred: {e}")
        if attempt < retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("All retry attempts failed. Exiting.")
            raise e