from dotenv import dotenv_values
from openai import OpenAI
from tabulate import tabulate
import pandas as pd
import json

# Load environment variables
config = dotenv_values(".env")
client = OpenAI(api_key=config['OPENAI_API_KEY'])

# Function to extract product information from PDF text using OpenAI API
def extract_product_info_from_text(text):
    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content":  f"""
                            Extract and structure product information from the PDF invoice files. Specifically, identify the following details for each product listed in the invoice:
                            - Barcode (A unique identifier for the product, some products may not have a barcode. If they do not have a barcode, default to 'N/A')
                            - Product Name (The name of the product)
                            - Case Quantity (The number of cases ordered of the product)
                            - Units per Case (The number of units per case, this is usally found in the product name. Do not get this confused with the case quantity)
                            - Case Price (The price per case)
                            - Total Price (The total price for the amount ordered, this is usually Case Quantity * Case Price)
                            - Confidence Score (The confidence score of the extraction, a value between 0 and 1. This should be based on how confident you are that you got the case quantity and units per case correct as that is usally the hardest to detect)

                            Handle product descriptions with varied formats, such as 'Mysore Sandal soap (TRIO) (150g x 3) - 10 pkt', where the units per case is embedded differently (it would be 10 units per case in this product name). Ensure all derived quantities and prices are accurately calculated.
                            
                            The invoices given are badly structured many times so please look into details and extract the information accurately.

                            Output the data in a JSON object format, where each product's information is a separate object keyed by the product's barcode or a unique identifier.

                            Example of Expected Output for a Product:
                            {{
                            "barcode": "19127",
                            "product_name": "Telephone Isabgol 200gms x 5 pcs",
                            "case_quantity": "30",
                            "units_per_case": "5",
                            "case_price": "$25.00",
                            "total_price": "$750.00",
                            "confidence_score": "0.95"

                            }}
                            Do not include unrelated details from the invoice. Pay special attention to products with non-standard packaging formats and ensure accurate extraction. 
                            Only give me the JSON objects with the product information, I do not want any thank you message or extra information.
                            Here is the text {text}
                            """,
            }],
            model='gpt-4o-mini'
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return None
    
# Function to extract product information from string response that is in JSON format and make it into table with tabulate
def extract_product_info_from_response(response):
    if '```json' or '```' in response:
        response = response.replace('```json', '').replace('```', '')
    try:
        # Load JSON data
        if isinstance(response, str):
            product_info = json.loads(response)
        else:
            product_info = response
        
        # Create a DataFrame
        df = pd.DataFrame(product_info).T  # Transpose to make each product a row
        
        # Convert numeric columns to integers
        df['case_quantity'] = df['case_quantity'].astype(int)
        df['units_per_case'] = df['units_per_case'].astype(int)

        # Add tota_units and unit_cost columns
        df['total_units'] = df['case_quantity'] * df['units_per_case']
        df['unit_cost'] = df['case_price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float) / df['units_per_case']

        # Round the unit cost to two decimal places and add a dollar sign
        df['unit_cost'] = '$' + df['unit_cost'].round(2).astype(str)

        
        # Print table using Tabulate
        return tabulate(df, headers='keys', tablefmt='fancy_grid')
    except Exception as e:
        print(e)
        return None
    