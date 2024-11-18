# Upload and Download Files into Citesphere

## Setup
There are two notebooks in this folder: `Upload` and `Download`. Before using these notebooks, you should create a new virtual environment (`python -m venv ven` and then `source venv/bin/active`). Then install the requirements (`pip install -r requirements`).

## Citesphere Token
You will need a Citesphere access token to use these notebooks.

## Upload
Set the variables as described in the notebook and then run all cells. New items created in Zotero will get the filename as title and be of type "Document".

## Download
This notebook will download the extracted text of all files in a group. If a file with the same filename already exists in the folder to download files into, then files will be overwritten.