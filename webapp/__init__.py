from flask import Flask #import Flask
from flask_mysqldb import MySQL #import mySQL
import boto3 #Import AWS services

# Flask app
app = Flask(__name__)

# For MYSQL
app.config['MYSQL_USER'] = 'sql3391048' 
app.config['MYSQL_PASSWORD'] = 'RnvlkfUtVK'
app.config['MYSQL_HOST'] = 'sql3.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql3391048'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# For Flask WTF
app.config['SECRET_KEY'] = "secretsecrets"

# Mysql database
db = MySQL(app)

# Amazon AWS s3 bucket (for image storing)
s3 = boto3.client('s3')

from webapp.config import config 
conf = config()

# Our code for creating avatars
from webapp.AvatarCreator import AvatarCreator
avc = AvatarCreator() #creates a new avatar object
# The webpage routes
from webapp import routes
