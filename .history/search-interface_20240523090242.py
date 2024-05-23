import pymongo
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import ttk

# Load variables from .env file
load_dotenv()

# MongoDB Atlas connection string
connection_string = os.getenv("CONNECTION_STRING")

# Connect to MongoDB Atlas
client = MongoClient(connection_string)
db = client["pdf_database"]
collection = db["pdf_collection"]

# Create a TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words="english")

def search_documents(query):
    # Preprocess the query
    query_vector = vectorizer.transform([query]).toarray()[0]
    
    # Retrieve all documents from the database
    documents = list(collection.find())
    
    # Calculate the cosine similarity between the query vector and document vectors
    similarities = []
    for document in documents:
        document_vector = document["vector"]
        similarity = cosine_similarity([query_vector], [document_vector])[0][0]
        similarities.append((document["filename"], similarity))
    
    # Sort the documents by similarity score in descending order
    sorted_documents = sorted(similarities, key=lambda x: x[1], reverse=True)
    
    return sorted_documents

def search_button_click():
    query = query_entry.get()
    search_results = search_documents(query)
    
    # Clear previous search results
    result_text.delete('1.0', tk.END)
    
    # Display search results in the text widget
    for i, (filename, similarity) in enumerate(search_results, start=1):
        result_text.insert(tk.END, f"{i}. {filename} (Similarity: {similarity:.2f})\n")

# Create the main window
window = tk.Tk()
window.title("PDF Library Search")

# Create and pack the query label and entry
query_label = ttk.Label(window, text="Search Query:")
query_label.pack()
query_entry = ttk.Entry(window)
query_entry.pack()

# Create and pack the search button
search_button = ttk.Button(window, text="Search", command=search_button_click)
search_button.pack()

# Create and pack the search result text widget
result_text = tk.Text(window)
result_text.pack()

# Start the Tkinter event loop
window.mainloop()

# Close the MongoDB connection
client.close()