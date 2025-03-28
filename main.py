from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

# Path to the service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Change this to your actual path

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate using the service account with the correct scopes
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# ID of the Google Sheet
SPREADSHEET_ID = 'your_spreadsheet_id'  # Change this to your actual spreadsheet ID

# Open the Google Sheet by its ID
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.sheet1  # or use sheet.worksheet('Sheet1') for a named sheet

# Define a Pydantic model for the input
class SheetData(BaseModel):
    values: List[List[str]]

@app.get("/read")
async def read_sheet():
    try:
        # Reading from the Google Sheet
        values = worksheet.get_all_values()
        return {"values": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/write")
async def write_sheet(data: SheetData):
    try:
        # Writing to the Google Sheet
        worksheet.update('A1', data.values)  # Update starting from cell A1
        return {"message": "Sheet updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/registration")
async def search_by_registration(regno: str):
    try:
        # Retrieve all values from the sheet
        values = worksheet.get_all_values()
        
        # Find the row that matches the registration number
        matching_row = None
        for row in values:
            if row[2].strip() == regno.strip():  # Assuming registration number is in the third column (index 2)
                matching_row = row
                break

        if not matching_row:
            raise HTTPException(status_code=404, detail=f"No row found with registration number: {regno}")

        return {"matching_row": matching_row}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
