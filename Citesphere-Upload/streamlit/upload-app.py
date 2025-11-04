import streamlit as st
from streamlit_oauth import OAuth2Component

import os
import requests
import glob

st.title('Uploads Files into Citesphere')
st.markdown('''
            To upload files to Citesphere, do the following: 
            
            - Click "Authorize" and login and grant access to Citesphere.
            - If the files you want to upload are not in a folder next to the code for this app called "files" change the folder name.
            - Enter the group id of the Zotero group you want to upload files into.
            - Enter the base URL of the Citesphere instance you want to upload files to. Ensure the URL has not trailing slash.
            - Click "Upload Files."
            ''')

BASE_URL = os.environ.get('BASE_URL')
AUTHORIZE_URL = f"{BASE_URL}/api/oauth/authorize"
TOKEN_URL = f"{BASE_URL}/api/oauth/token"
REFRESH_TOKEN_URL = f"{BASE_URL}/api/oauth/authorize"
REVOKE_TOKEN_URL = ""
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
SCOPE = os.environ.get('SCOPE')

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


def submit_file(data, file_path):
    headers = {'Authorization': f'Bearer {st.session_state.token['access_token']}'}
    try:
        file_obj = open(file_path, 'rb')  # Open the file
        files = [(os.path.basename(file_path), file_obj)]

        request_files = [('files', (name, file, 'application/pdf')) for name, file in files]
        response = requests.post(API_URL, headers=headers, data=data, files=request_files)
        log.write(f"{os.path.basename(file_path).split('/')[-1]}... {response.status_code}")
        #log.write(response.text) #uncomment this to see response body (e.g. for troubleshooting)
    except Exception as e:
        log.write(f"[ERROR] -------- Error during API request with {file_path}: {e}")
    finally:
        for _, file in files:
            file.close()  

def import_files():
    # find all PDF files in the folder to upload from
    glob_files = glob.glob(os.path.join(st.session_state.folder_name, '*.pdf'))
    total_files = len(glob_files)
    current_index = 0
    for path in glob_files:
        current_index+=1
        progress_bar.progress(current_index/total_files, text="Uploading files..." + os.path.basename(path).split('/')[-1])
        #log.write(f"Submitting {os.path.basename(path).split('/')[-1]} to {API_URL}")
        data = {
            'title': os.path.basename(path).split('/')[-1],
            'itemType': 'DOCUMENT',
        }
        submit_file(data, path)
    progress_bar.progress(100, "Upload done.")

col1, log = st.columns(2)

# Streamlis Elements
# enter variables we need
col1.text_input("Folder name that has files", value="files", key="folder_name")
col1.text_input("Group ID to Import Into", key="group_id")
col1.text_input("Citesphere API Base URL (remove trailing slash)", key="citesphere_base_url")

col1.button("Upload Files", type="primary", on_click=import_files)

progress_bar = log.progress(0, text='Click "Upload Files" to start uploading.')

API_URL = f"{st.session_state.citesphere_base_url}/api/v1/groups/{st.session_state.group_id}/items/create"

