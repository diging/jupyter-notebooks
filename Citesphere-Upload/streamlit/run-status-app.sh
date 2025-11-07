python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

source app.config
streamlit run status-app.py 