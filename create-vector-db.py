import os
import csv
import pymongo
from pymongo import MongoClient
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Specify the folder path containing the PDF files (UNC path format)
folder_path = os.getenv("FOLDER_PATH")

# Specify the CSV file path containing the extracted metadata
csv_file = os.getenv("CSV_FILE")

# MongoDB Atlas connection string
connection_string = os.getenv("CONNECTION_STRING")

# Connect to MongoDB Atlas
client = MongoClient(connection_string)
db = client["pdf_database"]
collection = db["pdf_collection"]

# Read the metadata from the CSV file
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    metadata_list = list(reader)

# Create a TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words="english")

# Extract text content from PDF files and generate vectors
pdf_data = []
for metadata in metadata_list:
    filename = metadata["Filename"]
    file_path = os.path.join(folder_path, filename)
    
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            
            # Preprocess the text content
            preprocessed_text = preprocess_text(text_content)
            
            # Generate vector representation
            vector = vectorizer.fit_transform([preprocessed_text]).toarray()[0]
            
            # Combine metadata and vector
            pdf_data.append({
                "filename": filename,
                "metadata": metadata,
                "vector": vector.tolist()
            })
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

# Insert the PDF data into MongoDB Atlas
collection.insert_many(pdf_data)

print("Vector database created successfully.")

def preprocess_text(text):
    # Perform text preprocessing steps (e.g., remove stopwords, punctuation, etc.)
    # Return the preprocessed text
    # ...