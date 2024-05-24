import os
import csv
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError, EmptyFileError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Specify the folder path containing the PDF files (UNC path format)
folder_path = os.getenv("FOLDER_PATH")
if not folder_path:
    raise ValueError("Environment variable FOLDER_PATH is not set")

# Specify the output CSV file path
output_file = os.getenv("OUTPUT_FILE")
if not output_file:
    raise ValueError("Environment variable OUTPUT_FILE is not set")

# CSV header
header = [
    "Filename",
    "Title",
    "Author",
    "Subject",
    "Keywords",
    "Creator",
    "Producer",
    "Creation Date",
    "Modification Date",
    "Error",
]

# Open the output CSV file in write mode
with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)

    # Write the header to the CSV file
    writer.writerow(header)

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)

            try:
                # Open the PDF file
                with open(file_path, "rb") as file:
                    try:
                        # Create a PDF reader object
                        pdf_reader = PdfReader(file)

                        # Get the metadata dictionary
                        metadata = pdf_reader.metadata

                        # Initialize metadata fields with empty strings
                        title = author = subject = keywords = creator = producer = (
                            creation_date
                        ) = modification_date = error = ""

                        # Extract specific metadata fields
                        if metadata is not None:
                            title = metadata.get("/Title", "")
                            author = metadata.get("/Author", "")
                            subject = metadata.get("/Subject", "")
                            keywords = metadata.get("/Keywords", "")
                            creator = metadata.get("/Creator", "")
                            producer = metadata.get("/Producer", "")
                            creation_date = metadata.get("/CreationDate", "")
                            modification_date = metadata.get("/ModDate", "")

                    except PdfReadError as e:
                        error = f"PdfReadError: {str(e)}"
                    except EmptyFileError as e:
                        error = f"EmptyFileError: {str(e)}"

                # Write the metadata to the CSV file
                row = [
                    filename,
                    title,
                    author,
                    subject,
                    keywords,
                    creator,
                    producer,
                    creation_date,
                    modification_date,
                    error,
                ]
                writer.writerow(row)

            except Exception as e:
                error = f"Exception: {str(e)}"
                # Write the filename and fill metadata fields with empty strings in case of an error
                row = [filename, "", "", "", "", "", "", "", "", error]
                writer.writerow(row)

            # Print the error message, if any, with safe encoding handling
            if error:
                print(f"Error processing {filename}: {error}".encode('ascii', 'replace').decode('ascii'))

print("Metadata extraction completed. Results saved to", output_file)
