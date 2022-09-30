from dotenv import load_dotenv
import os
load_dotenv()
username=os.getenv("USER_NAME")
password=os.getenv("PASSWORD")
ip_adresse=os.getenv("IP_ADRESSE")
port=os.getenv("PORT")
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

database_path ='postgresql://{}:{}@{}:{}/trivia'.format(username , password , ip_adresse , port)