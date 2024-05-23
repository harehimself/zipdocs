import os
import csv
import string
import nltk
import pymongo
from pymongo import MongoClient
from PyPDF2 import PdfReader
from PyPDF2.errors import EmptyFileError, PdfReadError
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from dotenv import load_dotenv
import sys

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

# Download the 'punkt' resource
nltk.download('punkt')

# Download the 'stopwords' resource
nltk.download('stopwords')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    # Remove digits
    text = "".join(char for char in text if not char.isdigit())
    
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Stemming or Lemmatization
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    tokens = [stemmer.stem(token) for token in tokens]
    # tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Join the tokens back into a string
    preprocessed_text = " ".join(tokens)
    
    return preprocessed_text

def print_unicode_error(error_message):
    print(error_message.encode(sys.stdout.encoding, errors='replace').decode('utf-8'))

# Extract text content from PDF files and generate vectors
pdf_data = []
for metadata in metadata_list:
    filename = metadata["Filename"]
    file_path = os.path.join(folder_path, filename)
    
    try:
        with open(file_path, "rb") as file:
            try:
                pdf_reader = PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    try:
                        text_content += page.extract_text()
                    except Exception as e:
                        print_unicode_error(f"Skipping page with error in {filename}: {str(e)}")
                
                # Preprocess the text content
                preprocessed_text = preprocess_text(text_content)
                
                if preprocessed_text.strip():
                    # Generate vector representation
                    vector = vectorizer.fit_transform([preprocessed_text]).toarray()[0]
                    
                    # Combine metadata and vector
                    pdf_data.append({
                        "filename": filename,
                        "metadata": metadata,
                        "vector": vector.tolist()
                    })
                else:
                    print_unicode_error(f"Skipping document with empty vocabulary: {filename}")
            except (EmptyFileError, PdfReadError) as e:
                print_unicode_error(f"Skipping file with PDF reading error: {filename}")
            except ValueError as e:
                if "empty vocabulary" in str(e):
                    print_unicode_error(f"Skipping document with empty vocabulary: {filename}")
                else:
                    raise
    except Exception as e:
        error_message = f"Error processing {filename}: {str(e)}"
        print_unicode_error(error_message)

# Insert the PDF data into MongoDB Atlas
collection.insert_many(pdf_data)

print("Vector database created successfully.")
