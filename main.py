import pandas as pd
from io import StringIO
from pdf_extract import extract_text_from_pdf  # make sure to import your PDF extraction function
from openai_prompt import extract_product_info_from_text, extract_product_info_from_response  # import your processing functions
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import time


file_path = ''

# Setup the GUI
root = tk.Tk()
root.title("PDF Data Extractor")
root.minsize(500, 600)
# File path display
file_path_display = tk.Label(root, text="No file selected", wraplength=300)
file_path_display.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Upload button
def upload_action():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    file_path_display.config(text=f"File: {file_path}")

upload_button = tk.Button(root, text="Upload PDF", command=upload_action)
upload_button.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

# Process button and timer
def process_file():
    start_time = time.time()  # Start timer
    pdf_text = extract_text_from_pdf(file_path)  # Extract text from the selected PDF
    api_response = extract_product_info_from_text(pdf_text)  # Process text to get structured data
    table = extract_product_info_from_response(api_response)  # Get the table in fancy_grid format
    
    # Display the table in the text area
    table_display.delete('1.0', tk.END)  # Clear previous content
    table_display.insert(tk.INSERT, table)
    
    # Update process button text to show elapsed time
    elapsed_time = time.time() - start_time
    process_button.config(text=f"Processed in {elapsed_time:.2f} seconds")

process_button = tk.Button(root, text="Process File", command=process_file)
process_button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

# Text area for table display
table_display = scrolledtext.ScrolledText(root, width=70, height=20)
table_display.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

# Download button
def download_table():
    # Extracting text from the text area (alternative: maintain a DataFrame)
    table_text = table_display.get('1.0', tk.END)
    # Convert the table text back to a DataFrame (assuming it is comma-separated)
    df = pd.read_csv(StringIO(table_text), sep=',')
    save_path = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension=".csv")
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Table saved to {save_path}")

download_button = tk.Button(root, text="Download CSV", command=download_table)
download_button.grid(row=4, column=0, sticky="ew", padx=10, pady=10)

# Configure the grid to resize
root.grid_columnconfigure(0, weight=1)  # Makes the column expandable
root.grid_rowconfigure(3, weight=1)  # Makes the row containing the table_display expandable
root.mainloop()
