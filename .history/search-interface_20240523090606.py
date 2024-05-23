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

def search_documents(query, filters, sort_option):
    # Preprocess the query
    query_vector = vectorizer.transform([query]).toarray()[0]
    
    # Apply filters
    filter_conditions = []
    if "author" in filters:
        filter_conditions.append({"metadata.Author": {"$regex": filters["author"], "$options": "i"}})
    if "title" in filters:
        filter_conditions.append({"metadata.Title": {"$regex": filters["title"], "$options": "i"}})
    if "subject" in filters:
        filter_conditions.append({"metadata.Subject": {"$regex": filters["subject"], "$options": "i"}})
    
    # Retrieve documents from the database based on filters
    if filter_conditions:
        documents = list(collection.find({"$and": filter_conditions}))
    else:
        documents = list(collection.find())
    
    # Calculate the cosine similarity between the query vector and document vectors
    similarities = []
    for document in documents:
        document_vector = document["vector"]
        similarity = cosine_similarity([query_vector], [document_vector])[0][0]
        similarities.append((document["filename"], similarity, document["metadata"]))
    
    # Sort the documents based on the selected option
    if sort_option == "Similarity":
        sorted_documents = sorted(similarities, key=lambda x: x[1], reverse=True)
    elif sort_option == "Author":
        sorted_documents = sorted(similarities, key=lambda x: x[2].get("Author", ""))
    elif sort_option == "Title":
        sorted_documents = sorted(similarities, key=lambda x: x[2].get("Title", ""))
    else:
        sorted_documents = similarities
    
    return sorted_documents

def search_button_click():
    query = query_entry.get()
    filters = {
        "author": author_filter_entry.get(),
        "title": title_filter_entry.get(),
        "subject": subject_filter_entry.get()
    }
    sort_option = sort_var.get()
    
    search_results = search_documents(query, filters, sort_option)
    
    # Clear previous search results
    result_text.delete('1.0', tk.END)
    
    # Display search results in the text widget
    for i, (filename, similarity, metadata) in enumerate(search_results, start=1):
        result_text.insert(tk.END, f"{i}. {filename} (Similarity: {similarity:.2f})\n")
        result_text.insert(tk.END, f"   Author: {metadata.get('Author', '')}\n")
        result_text.insert(tk.END, f"   Title: {metadata.get('Title', '')}\n")
        result_text.insert(tk.END, f"   Subject: {metadata.get('Subject', '')}\n")
        result_text.insert(tk.END, "\n")

# Create the main window
window = tk.Tk()
window.title("PDF Library Search")

# Create and pack the query label and entry
query_label = ttk.Label(window, text="Search Query:")
query_label.pack()
query_entry = ttk.Entry(window)
query_entry.pack()

# Create and pack the filter labels and entries
filter_frame = ttk.Frame(window)
filter_frame.pack()

author_filter_label = ttk.Label(filter_frame, text="Author:")
author_filter_label.grid(row=0, column=0)
author_filter_entry = ttk.Entry(filter_frame)
author_filter_entry.grid(row=0, column=1)

title_filter_label = ttk.Label(filter_frame, text="Title:")
title_filter_label.grid(row=1, column=0)
title_filter_entry = ttk.Entry(filter_frame)
title_filter_entry.grid(row=1, column=1)

subject_filter_label = ttk.Label(filter_frame, text="Subject:")
subject_filter_label.grid(row=2, column=0)
subject_filter_entry = ttk.Entry(filter_frame)
subject_filter_entry.grid(row=2, column=1)

# Create and pack the sort option label and radio buttons
sort_label = ttk.Label(window, text="Sort By:")
sort_label.pack()

sort_var = tk.StringVar(value="Relevance")
sort_similarity_radio = ttk.Radiobutton(window, text="Similarity", variable=sort_var, value="Similarity")
sort_similarity_radio.pack()
sort_author_radio = ttk.Radiobutton(window, text="Author", variable=sort_var, value="Author")
sort_author_radio.pack()
sort_title_radio = ttk.Radiobutton(window, text="Title", variable=sort_var, value="Title")
sort_title_radio.pack()

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