from webapp import db, app, s3, avc, conf
from flask import request
import logging
import boto3
import webbrowser
from botocore.exceptions import ClientError

# This method is used to update values in the User table on the SQL server
def updateUserTable(variable,value):
    value = "'" + value + "'" # Turns the value into a string that can be concatenated
    id = str(conf.user_id) # Gets the user id into a string form
    print("Changing " +variable+ " To " +value) 
    cur = db.connection.cursor() # Establish a connection to the SQL server
    cur.execute('''UPDATE Users SET '''+variable+'''='''+value+''' WHERE user_id='''+id) # Update the value
    db.connection.commit() # Commits the changes, otherwise no change would occur
    cur.close() # Closes the connection to the SQL server

# This method is used to download data for either string variables or all the variables in the user table on the SQL server
def getStringUserTable(variable):
    id = str(conf.user_id) # Gets the user id into a string form
    if variable == '*': # If the variable is an asterisk this means all of the information for the user
        print("Getting all information for user-id " + id)
        cur = db.connection.cursor() # Establish a connection to the SQL server
        cur.execute('''SELECT * FROM Users WHERE user_id = '''+id) # Download all of the data for the user using this device
        results = cur.fetchall() # Set results equal to the the downloaded data
        output = results[0] # Set the output as the first object in the results object. 
    else:
        print("Getting " + variable + " for user-id = " + id)
        cur = db.connection.cursor() #Establish a connection to the SQL server
        cur.execute('''SELECT ''' + variable + ''' FROM Users WHERE user_id = '''+id) # Download the data for the given variable
        results = cur.fetchall() # Set results equal to the the downloaded data
        output = str(results[0][variable]) # Set the output as the first object, and remove the lable on it using [variable]
    return output # Return the output from the method

# This method is used to download data for the int variables in the user table on the SQL server
def getIntUserTable(variable):
    id = str(conf.user_id)
    print("Getting " + variable + " for user-id = " + id)
    cur = db.connection.cursor() #Establish a connection to the SQL server
    cur.execute('''SELECT ''' + variable + ''' FROM Users WHERE user_id = '''+id)
    results = cur.fetchall()
    output = results[0][variable]
    return output

# This method is used to determine whether the user's avatar is custom or one of the defaults.
# If the avatar is default then it also determines which avatar it is. 
def getAvatarName(id):
    print("Getting user's avatar...")
    
    output = getStringUserTable('AvatarFace')
    if output == 'custom':
        avc.custom_face = True
        print("user character is custom")
    else:
        avc.character = output
        print("user character is", avc.character)

# This method is used to upload the custom avatar image to the AWS server
def uploadCustomImg(img, bucket, object_name):
    print("Uploading Image")
    #Upload a file to an S3 bucket

    #:param file_name: File to upload
    #:param bucket: Bucket to upload to
    #:param object_name: S3 object name. If not specified then file_name is used
    #:return: True if file was uploaded, else False

    #file_name = str(img)
    file_name = img
     # If S3 object_name was not specified, use file_name
    #if object_name is None:
    #    object_name = file_name
    response = s3.upload_file(file_name, bucket, object_name)
    
    #try:
        
    #except ClientError as e:
    #    logging.error(e)
    #    return False
    #return True

# This method is used to change the password for a user
def changePassword(newPassword, confirmNewPassword):
    print("Changing Password")

def modifyMedications(newMeds):
    print("Changing Medications")

# This method is used to download the image of a given medication from the AWS server 
def medImage(name):
    print("Downloading Image of " + name)
    s3.download_file('tm-images-1', 'medication-images/'+name+'.png', 'webapp/static/medications/'+name+'.png')

def pillDispensed():
    print("Pill Dispensed")

# This method is used to determine if the user is currently recieving a video call from their doctor
def recieveCall():
    output = getIntUserTable('zoom') #Get the zoom value for the given user
    print(output)
    if output == 1: # If the zoom value is 1, the user is being called by their doctor
        print("Yes Call")
        name = getStringUserTable('firstname') # Get the firstname of the user 
        print(name)
        url = 'https://meet.jit.si/' + name # Create a unique meeting url using the firstname of the user
        webbrowser.open_new_tab(url) # Open the unique meeting in a new tab
    else: # If the zoom value is 0, the user is not being called by their doctor. 
        print("No Call")