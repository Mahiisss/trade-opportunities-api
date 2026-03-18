from fastapi import Header, HTTPException
import os
import logging

API_KEY = os.getenv("API_KEY", "1234mahi")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        logging.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    return x_api_key