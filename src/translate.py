import json
import os
import time
import asyncio
import aiohttp

import requests
from dotenv import load_dotenv

load_dotenv()
bhashini_api_key = os.environ.get("BHASHINI_API_KEY")

async def translate_and_report_progress(i, line, total_lines, progress_lock):
    translated_line = await translate_text_bhashini(line)
    async with progress_lock:
        progress = (i + 1) / total_lines * 100        
    return translated_line[0]

async def parallel_translation(all_text):
    lines = all_text.split('\n')
    total_lines = len(lines)
    progress_lock = asyncio.Lock()
    
    # Create a list of tasks for each line
    tasks = [
        translate_and_report_progress(i, line, total_lines, progress_lock)
        for i, line in enumerate(lines)
    ]
    
    # Gather results from the tasks
    translated_lines = await asyncio.gather(*tasks)
    translated_text = '\n'.join(translated_lines)
    return translated_text

async def translate_text_bhashini(input_text, source="hi", target="en"):
    if input_text == "":
        return "",""
    
    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    payload = json.dumps(
        {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source,
                            "targetLanguage": target,
                        },
                        "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                    },
                }
            ],
            "inputData": {"input": [{"source": input_text}]},
        }
    )
    headers = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": bhashini_api_key,
        "Content-Type": "application/json",
    }

    retries = 0
    max_retries = 5
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        while retries < max_retries:
            try:
                async with session.post(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        translated_output = response_data["pipelineResponse"][0]["output"][0]["target"]
                        end_time = time.time()
                        return translated_output, retries, end_time - start_time
                    else:
                        print(f"Request failed with status code {response.status}. Retrying...")
                        retries += 1
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                retries += 1

    end_time = time.time()
    return "Translation failed after maximum retries.", max_retries, end_time - start_time
