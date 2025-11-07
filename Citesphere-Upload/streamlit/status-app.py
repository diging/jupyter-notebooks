import streamlit as st
from streamlit_oauth import OAuth2Component

import os
import requests, time, traceback
from collections import Counter
import pandas as pd

st.title('Check Status of Files Uploaded into Citesphere')
st.markdown('''
            To check the status of files uploaded into Citesphere, do the following: 
            
            - Click "Authorize" and login and grant access to Citesphere.
            - Enter the group id of the Zotero group you want to upload files into.
            - Click "Check Status."
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

# once we have a token, set it
TOKEN = None
if "token" in st.session_state:
    TOKEN = st.session_state.token['access_token']

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

# Streamlis Elements
col1, log = st.columns(2)

# enter variables we need
GROUP_ID = col1.text_input("Group ID to check status for", key="group_id")



# get groups
def get_items(page):
    ITEMS_API_URL = f"{BASE_URL}/api/v1/groups/{GROUP_ID}/items"
    headers = {'Authorization': f'Bearer {TOKEN}'}
    print(ITEMS_API_URL)
    response = requests.get(ITEMS_API_URL + "?page="+str(page), headers=headers)
    print(response)
    return response.json()

def check_status():

    with log.status("Checking status...", expanded=True) as status:
        processed_success_count = st.empty()
        processed_success_count.write(f"Processed succesfully: 0")

        processed_failure_count = st.empty()
        processed_failure_count.write(f"Processing failed: 0")

        processed_running_count = st.empty()
        processed_running_count.write(f"Still processing: 0")

        log_scroll = log.container(height=400)

        page=0
        while(True):
            page = page+1
            counter = Counter(success=0, failure=0, processing=0, total=0)
            
            items = get_items(page)
            if not "items" in items or not items['items']:
                print("no more items, done.")
                break

            print("Page " + str(page))
            if "error" in items:
                print(items)
            
            # get file ids to download
            for item in items['items']:
                
                uploads = item['gilesUploads'] if 'gilesUploads' in item and item['gilesUploads'] else []

                # print item key and title if it has giles uploads
                if uploads:
                    log_scroll.write(f'**{item["key"]}: {item["title"] if item["title"] else "No title"}**')
                    log_scroll.write(f'*Number of uploaded files: {len(uploads)}*')

                for upload in uploads:
                    counter["total"] += 1
                    status_value = upload["documentStatus"]
                    if status_value == "COMPLETE":
                        counter["success"] += 1
                        processed_success_count.write(f"Processed succesfully: {counter["success"]}")
                    elif status_value == "FAILED":
                        counter["failure"] += 1
                        processed_failure_count.write(f"Processing failed: {counter["failure"]}")
                    else:
                        counter["processing"] += 1
                        processed_running_count.write(f"Still processing: {counter["processing"]}")
                    try:
                        filename = upload["uploadedFile"]["filename"] if upload["uploadedFile"] else "No filename"
                        log_scroll.write(f'{filename}: {status_value}')
                    except Exception as e:
                        log_scroll.write("Encountered an error!")
                        log_scroll.write(upload)
                        log_scroll.write(traceback.print_exc())

            # let's not make the next request right away
            time.sleep(0.5)
                

        df = pd.DataFrame([[counter["success"], counter["failure"], counter["processing"]]], columns=["Complete", "Failure", "Processing"])
        st.bar_chart(df, stack=False)

        status.update(
            label=f'Check complete! Total number of files: {counter["total"]}', state="complete", expanded=True
        )




col1.button("Check status", type="primary", on_click=check_status)

