from web3 import Web3, __version__ as web3_version
import requests
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

print("Web3 version:", web3_version)
print("Requests version:", requests.__version__)
print("SQLAlchemy version:", create_engine("sqlite:///:memory:"))
load_dotenv()
print("python-dotenv loaded!")