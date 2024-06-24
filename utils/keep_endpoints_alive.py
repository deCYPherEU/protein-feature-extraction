import requests
import os
from dotenv import load_dotenv
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv(".env")

time_to_sleep = 10 # min


# check if everything is here
hf_key = os.getenv("HF_API_KEY")

def keep_esm_alive():
    url = "https://ip4ue7gflyjw3miy.eu-west-1.aws.endpoints.huggingface.cloud"
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"}
    data = {"inputs": "MAGLKPEVPLHDGINKFGKSDFAGQEGPKIVTTTD"}
    response = requests.post(url, headers=headers, json=data)
    logging.info("esm: %s", response.status_code)
    return response.status_code


def keep_unikp_alive():
    url = "https://sccmnejsco4ndxwt.eu-west-1.aws.endpoints.huggingface.cloud"
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"}
    data = {
        "inputs": {
            "sequence": "MAGLKPEVPLHDGINKFGKSDFAGQEGPKIVTTTD",
            "smiles": "CC(=O)O"
        }
    }
    response = requests.post(url, headers=headers, json=data)
    logging.info("unikp: %s", response.status_code)


while True:
    keep_esm_alive()
    keep_unikp_alive()
    time.sleep(60 * time_to_sleep)



