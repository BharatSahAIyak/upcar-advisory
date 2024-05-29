import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
bhashini_api_key = os.environ.get("BHASHINI_API_KEY")


def translate_text_bhashini(input_text, source="hi", target="en"):
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
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, data=payload)
            # Check if the request was successful
            if response.status_code == 200:
                translated_output = json.loads(response.text)["pipelineResponse"][0][
                    "output"
                ][0]["target"]
                end_time = time.time()
                return translated_output, retries, end_time - start_time
            else:
                print(
                    f"Request failed with status code {response.status_code}. Retrying..."
                )
                retries += 1
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            retries += 1

    end_time = time.time()
    return (
        "Translation failed after maximum retries.",
        max_retries,
        end_time - start_time,
    )
