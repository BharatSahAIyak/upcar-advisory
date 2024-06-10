import shutil
import requests
import time
import tempfile
from src.scraper import scraper, move_json_to_history, download_pdf
from src.ocr import get_hindi_text, merge_lines_between_empty_lines
from src.translate import translate_text_bhashini, parallel_translation
from src.llm import (
    call_and_save_response,
    validate_response,
    save_response,
    refine_response
)
import logging
from openai import OpenAI
from dotenv import load_dotenv
from prompt import prompt
from jsonschema import validate, ValidationError
import os
import json
import asyncio
from datetime import datetime
load_dotenv()

webhook_url=os.environ.get("WEBHOOK_URL")

def get_crop_advisory():
    temp_dir = tempfile.mkdtemp()

    try:
        data = scraper()
    except Exception as e:
        logging.error(f"Error getting districts data: {e}")
        print("Error scraping website")

    # move latest to history. 
    try:
        move_json_to_history()
    except Exception as e:
        print("Error moving latest to history",e)

    print("Scraping PDF...")
    pdf_file = download_pdf(data.get('download_url'), temp_dir)
    print("OCR...")
    hindi_text = merge_lines_between_empty_lines(get_hindi_text(pdf_file))
    print("Translating...")
    english_text = asyncio.run(parallel_translation(hindi_text))
    print("GPT call...")
    date=data["date"]
    is_inconsistent, llm_response, e = call_and_save_response(english_text,date)

    retry=1
    
    # Iterating again on inconsistent districts
    while retry<=3 and is_inconsistent:
        resp=refine_response(llm_response,e)
        is_inconsistent=resp[0]
    
    # Sending update through webhook
    try:
        data={
            "is_inconsistent":str(is_inconsistent),
            "e":e,
            "time":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        formatted_string = json.dumps(data, indent=4)
        payload={
            "content":str(formatted_string)
        }
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Webhook notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print("Error sending webhook notification:", e)        

    # Removing temp dir
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error(f"Error removing temporary directory: {e}")

    return "SUCCESS"


if __name__ == "__main__":
    retries = 3
    retry_delay = 5

    for attempt in range(1, retries + 1):
        try:
            get_crop_advisory()    
            break
        except Exception as e:
            logging.error(f"Attempt {attempt}: An error occurred: {e}")
            if attempt < retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All retry attempts failed. Exiting.")
                raise e