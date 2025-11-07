# Upload and Download from Citesphere

This folder contains a few Streamlit apps to make uploading and downloading from Citesphere via script easier.

## Run the Upload App

First you will need to set some configurations:

- make a copy of `app.config-example` and name it `app.config`.
- change the following variables:
    - `BASE_URL`: The url of the Citesphere instance you are using.
    - `CLIENT_ID`: You will need to create an App in Citesphere. If you don't have access to this part of Citesphere, talk to the person who gave you access to Citesphere. Here, you will need the client id of the App created in Citesphere.
    - `CLIENT_SECRET`: The secret of the App that was created in Citesphere.

Once those configurations are set, you can run the upload app by calling `./run-upload-app.sh` from the command line. This should:

- create a Python virtual environment 
- install all required dependencies
- start the Streamlit app

In your browser, navigate to `http://localhost:8501` (this will probably have opened by itself). Make sure the files you want to have uploaded are in the `files` folder.

# Run the Status App

First you will need to set some configurations:

- make a copy of `app.config-example` and name it `app.config`.
- change the following variables:
    - `BASE_URL`: The url of the Citesphere instance you are using.
    - `CLIENT_ID`: You will need to create an App in Citesphere. If you don't have access to this part of Citesphere, talk to the person who gave you access to Citesphere. Here, you will need the client id of the App created in Citesphere.
    - `CLIENT_SECRET`: The secret of the App that was created in Citesphere.

Once those configurations are set, you can run the upload app by calling `./run-status-app.sh` from the command line. This should:

- create a Python virtual environment 
- install all required dependencies
- start the Streamlit app

In your browser, navigate to `http://localhost:8501` (this will probably have opened by itself). Follow the instructions in the app.

# Run the Download App

First you will need to set some configurations:

- make a copy of `app.config-example` and name it `app.config`.
- change the following variables:
    - `BASE_URL`: The url of the Citesphere instance you are using.
    - `CLIENT_ID`: You will need to create an App in Citesphere. If you don't have access to this part of Citesphere, talk to the person who gave you access to Citesphere. Here, you will need the client id of the App created in Citesphere.
    - `CLIENT_SECRET`: The secret of the App that was created in Citesphere.
    - `GILES_BASE_URL`: The url of the Giles instance you are using.

Once those configurations are set, you can run the upload app by calling `./run-download-app.sh` from the command line. This should:

- create a Python virtual environment 
- install all required dependencies
- start the Streamlit app

In your browser, navigate to `http://localhost:8501` (this will probably have opened by itself). Make sure the files you want to have uploaded are in the `files` folder.