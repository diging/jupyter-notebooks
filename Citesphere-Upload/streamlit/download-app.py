import streamlit as st
from streamlit_oauth import OAuth2Component

import os
import requests
import json
import time
import traceback

st.set_page_config(page_title="Download from Citesphere", layout="wide")
st.title('Download Files from Citesphere')
st.markdown('''To download files from Citesphere, do the following:   
                    
- Click "Authorize" and login and grant access to Citesphere.
- If you want to download files into a different folder than the default `download` folder, change the name in the input field.
- Enter the group id of the Zotero group you want to download files from.
- Click "Download Files."
            
 ''')

# OAuth2
BASE_URL = os.environ.get('BASE_URL')
AUTHORIZE_URL = f"{BASE_URL}/api/oauth/authorize"
TOKEN_URL = f"{BASE_URL}/api/oauth/token"
REFRESH_TOKEN_URL = f"{BASE_URL}/api/oauth/authorize"
REVOKE_TOKEN_URL = ""
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
SCOPE = os.environ.get('SCOPE')

GILES_ROOT = os.environ.get('GILES_BASE_URL')

# Download App
TOKEN = ''

# Create OAuth2Component instance
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

# Check if token exists in session state
if 'token' not in st.session_state:
    # If not, show authorize button
    result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
    if result and 'token' in result:
        # If authorization successful, save token in session state
        st.session_state.token = result.get('token')
        st.rerun()
else:
    # If token exists in session state, show the token
    token = st.session_state['token']
    st.json(token)
    if st.button("Refresh Token"):
        # If refresh token button is clicked, refresh the token
        token = oauth2.refresh_token(token)
        st.session_state.token = token
        st.rerun()

col1, log = st.columns(2)
spinner = log.empty()

col1.text_input("Folder name to download files into", value="download/", key="folder_name")
GROUP_ID = col1.text_input("Group ID to download texts from", key="group_id")

# the following should only be changed if the Citesphere API changes
ITEMS_API_URL = f"{BASE_URL}/api/v1/groups/{GROUP_ID}/items"
UPLOAD_BY_PROGRESS = f"{GILES_ROOT}/api/v2/files/upload/check/"
UPLOAD_ENDPOINT = f"{GILES_ROOT}/api/v2/resources/files/upload/"

# once we have a token, set it
TOKEN = None
if "token" in st.session_state:
    TOKEN = st.session_state.token['access_token']

# get groups
def get_items(page):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    print(ITEMS_API_URL)
    response = requests.get(ITEMS_API_URL + "?page="+str(page), headers=headers)
    return response.json()

def get_filename_from_response(response):
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition and 'filename=' in content_disposition:
        # Extract the filename value
        filename = content_disposition.split('filename=')[1].strip('"')
        return filename
    return None

def download_file(file_id):
    endpoint = f"{GILES_ROOT}/api/v2/resources/files/{file_id}/content"
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(endpoint, headers=headers)
    filename = f'{file_id}_{get_filename_from_response(response)}'

    # if we have a filename, we'll download the file
    # this will override files with the same name (file_id + filename) in the folder FOLDER_NAME!
    log.write(f"Trying to download {filename}.")
    if filename:
        folder_name = st.session_state["folder_name"]
        if not folder_name.endswith("/"):
            folder_name = folder_name + "/"
        with open(folder_name + filename, 'wb') as file:
            file.write(response.content)

def get_file_id_from_progress(progress_id):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    uploads = requests.get(UPLOAD_BY_PROGRESS + progress_id, headers=headers).json()
    file_ids = []

    # if processing in progress
    if 'msg' in uploads and "uploadId" in uploads:
        try:
            inprogress_uploads = requests.get(UPLOAD_ENDPOINT + uploads["uploadId"], headers=headers).json()
            for inprogress_upload in inprogress_uploads:
                if "extractedText" in inprogress_upload and inprogress_upload["extractedText"] and inprogress_upload["extractedText"]["id"]:
                    file_ids.append(inprogress_upload["extractedText"]["id"])
                else:
                    log.write(f"Can't download file for {progress_id}.")
        except Exception as e:
            log.write(inprogress_upload)
            log.write(traceback.print_exc())
    else:
        for upload in uploads:
            try:
                if "extractedText" in upload and upload["extractedText"] and upload["extractedText"]["id"]:
                    file_ids.append(upload["extractedText"]["id"])
                else:
                    log.write(f"Can't download file for {progress_id}.")
            except Exception as e:
                log.write(uploads)
                log.write(upload)
                log.write(traceback.print_exc())
            
    return file_ids

def execute_download():
    with spinner:
        with st.spinner("Downloading in progress...", show_time=True):
            # get info about files
            file_ids = []
            page=0
            while(True):
                page = page+1
                items = get_items(page)
                if not items['items']:
                    print("no more items, done.")
                    break
                print("Page " + str(page))
                if "error" in items:
                    print(items)
                
                # get file ids to download
                for item in items['items']:
                    time.sleep(0.5)
                    uploads = item['gilesUploads'] if 'gilesUploads' in item and item['gilesUploads'] else []
                    for upload in uploads:
                        try:
                            if 'extractedText' in upload and upload['extractedText']:
                                file_ids.append((upload['extractedText']['id']))
                            elif 'progressId' in upload and upload['progressId']:
                                file_ids = file_ids + get_file_id_from_progress(upload['progressId'])
                            else:
                                log.write("Could not download file for " + item['key'])
                        except Exception as e:
                            log.write("Encountered an error!")
                            log.write(upload)
                            log.write(traceback.print_exc())
            for file_id in file_ids:
                time.sleep(0.5)
                download_file(file_id)
        log.success(f"{len(file_ids)} processed. Done!")

col1.button("Download Files", type="primary", on_click=execute_download)



    