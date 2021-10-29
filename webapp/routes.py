from flask import Flask, render_template, send_file, request, jsonify, flash, redirect, url_for
from datetime import datetime
import os, time, cv2, http.client, webbrowser, shutil, imutils
from cv2 import VideoWriter, VideoWriter_fourcc
from imutils.video import VideoStream

from webapp import db, app, s3, avc, conf
from webapp.forms import AvatarForm, EditUserForm, CustomAvatarForm, LoginForm, CreateUserForm, UploadForm, MedicineForm, CallForm, MedConfForm
#from webapp.AvatarCreator import AvatarCreator
from webapp.DefaultImages import DefaultImages
from webapp.PillDispenser import PillDispenser
import webapp.pin_controller as pins

from webapp.helpers import getAvatarName, updateUserTable, uploadCustomImg, changePassword, modifyMedications, medImage, recieveCall, getStringUserTable, getIntUserTable
from werkzeug.utils import secure_filename

'''
helper function to create the headings on each page
'''
def template(title, text = "Default"):
    now = datetime.now() 
    fulldate = now.strftime("%X")
    today = now.strftime("%A") 
    scheduledDispenseTime = getStringUserTable('scheduled_dispense_time')
    templateData = {
        #'title' : title,
        'time' : fulldate,
        'dispenseTime' : scheduledDispenseTime,
        'text' : text,
        'date' : today,
        'pillBtn' : False
        }
    return templateData

'''
before the App is launched initialize the configuration file
'''
@app.before_first_request
def initialize():
    conf.initialize()

'''
home page with the time of loading(currently the time doesnt update)
'''
@app.route("/")
def home():
    print("home")
    templateData = template("Tele Pack")

    return render_template('HomePage.html',**templateData)

'''
view avatar message page
'''
@app.route("/avatarview")
def viewAvatar():
    loc = avc.prev_location.split('/')[-1]
    vid = "/avatar/" + loc
    print(vid)
    return render_template('AvatarView.html', vid=vid) # When the video ends return the user to the home page

'''
login page
'''
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm() # Creates a login form object from Forms.py
    cur = db.connection.cursor() # Creates a connection to the SQL Database

    if form.validate_on_submit():
        givenUsername = form.username.data # Use the username from the login form
        # Get all the data for the user with the given Username
        cur.execute('''SELECT * FROM Users WHERE username = "''' + givenUsername + '''"''') 
        results = cur.fetchall() # Set the data for the user equal to results
        if results == (): # If the results are blank that means the username is incorrect
            print('Please Enter Valid Username') 
        else: # If the results exist the username is correct
            newUserID = str(results[0]['user_id']) # Figure out the UserID for the given Username
            # Declares this device belongs to the user of the username in SQL
            cur.execute('''UPDATE Devices SET user_id = ''' + newUserID + ''' WHERE device_id = ''' + str(conf.device_id))
            print('Login Successful') 
            print('You are now logged into account number ' + newUserID)
            db.connection.commit() # Have to commit the change to the remote database
            cur.close() # Close the connection to the sql database
            conf.initialize() # Re-Initialize the configuration file with the new ID numbers
            return redirect(url_for('home')) # Send the User to home page
                

    return render_template('LoginPage.html', form = form)

'''
edit avatar page
'''
@app.route('/avatarselect', methods=['GET', 'POST'])
def avatarselect():
    print("Files Changing")
    DefaultImages() # Download the default images for the 4 default avatars
    av_form = AvatarForm() # Create the Algorithmia text to speech form object
    custom_avatar_form = CustomAvatarForm() # Create the Custom Avatar image form object
    current_vid = "/static/hi.mp4" # Load the current video as the default welcome video
    dayTime = datetime.now() # Get the time to create a unqiue code to append to the video
    nowTime = dayTime.strftime("%X, %Y")
    
    '''
    if av_form.validate_on_submit() and av_form.submitAvatar.data: #Check to see if the Text form is valid and has data
        #Get Name Variable from Java Script
        id = str(conf.user_id)
        print("Validated") 
        getAvatarName(id)            #Determine if the Users avatar is custom or one of the defaults
        location = avc.updateAvatarVid(av_form.text.data) #Download the Algorithmia video when it is generated to the location
        current_vid = "/avatar/" + location
        '''

    if custom_avatar_form.validate_on_submit() and custom_avatar_form.submitCustom.data: # Check to see if the custom avatar form is valid and has data
        print("Uploading Custom Avatar")
        filename = secure_filename(custom_avatar_form.file.data.filename) # Define the filename from the file submitted on the form
        uploaded_image = './webapp/static/custom_avatar.png' # Create the route for the new avatar image to go
        custom_avatar_form.file.data.save(uploaded_image) # Save the image from the form to the route
        upload_file_bucket = 'tm-images-1' # Define the bucket on AWS that will be uploaded to
        upload_file_key = 'users/' + str(conf.user_id) + '/custom_avatar.png' # Define the route on the AWS server that the image will be uploaded to
        uploadCustomImg(uploaded_image, upload_file_bucket, upload_file_key) # Upload the image to the AWS server
        print(filename)

    return render_template('AvatarSelect.html', form = custom_avatar_form, time = nowTime )

'''
helper route to send the avatar video to the webpage
'''
@app.route("/avatar/<video>")
def sendVideo(video):
    print("SEND VIDEO")
    print(video)
    return send_file(os.path.join(os.path.abspath('./webapp/static'), video))

'''
algorithmia page for making and viewing lipsync videos
'''
@app.route("/algorithmia", methods=['GET','POST'])
def algorithmia():
    av_form = AvatarForm()
    current_vid = "/static/hi.mp4" 
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")

    if av_form.validate_on_submit() and av_form.submitAvatar.data:
        # Get Name Variable from Java Script
        id = str(conf.user_id)
        print("Validated") 
        getAvatarName(id)            # Now nothing happens until the "create video" button is pressed
        location = avc.updateAvatarVid(av_form.text.data)
        current_vid = "/avatar/" + location

    return render_template('Algorithmia.html', av_form=av_form, vid=current_vid, time=nowTime)

'''
route to view all the information for the current user
'''
@app.route('/user')
def UserProfile():
    output = getStringUserTable('*') # Get all information for the current User
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")
    id = str(conf.user_id)

    print("Getting Username")
    user_name = output['username']
    if output['AvatarFace'] is None:
        avatar_face = 'Amy'
    else :
        avatar_face = output['AvatarFace']
    email = output['email']
    address = output['address']
    emergency_Contact = output['emergencycontact']
    emergency_Number = output['emergencycontactnumber']
    first_Name = output['firstname']
    last_Name = output['lastname']
    try:
        s3.download_file('tm-images-1', 'users/' + id + '/profilepic.jpg', 'webapp/static/profilePic.jpg')
        print('download success')
    except: 
        s3.download_file('tm-images-1', 'users/dummyUser/face.jpg', 'webapp/static/profilePic.jpg')
        print('download failed')
    

    return render_template('ViewProfile.html', username=user_name, avatar=avatar_face, 
                            email=email, address=address, emergCont=emergency_Contact, 
                            emergNumb=emergency_Number, firstName=first_Name, 
                            lastName=last_Name, time = nowTime)

'''
display all the contact information for TruMedicine
'''
@app.route('/contact')
def contact():
    return render_template('contact.html')

'''
webpage for making a new user profile
'''
@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    form = CreateUserForm()
    cur = db.connection.cursor()

    if request.method == 'POST':
        #if form.validate_on_submit():
        if form.validate():
            username = form.username.data 
            email = form.email.data
            firstName = form.firstName.data
            lastName = form.lastName.data
            address = form.address.data
            emergencyContactName = form.emergencyContactName.data
            emergencyContactNumb = form.emergencyContactNumb.data

            
            
            cur.execute('''SELECT `user_id` FROM `Users` ORDER BY `user_id` DESC''')
            #cur.execute('''SELECT * FROM `Users` WHERE 1''')
            results = cur.fetchall()[0]
            newUserID = str(results['user_id'] + 1)

            print("Inserting")
            cur.execute('''INSERT INTO `Users`(`user_id`, `username`, `profilepicpath`, `AvatarFace`, `email`, `address`, `emergencycontact`, `emergencycontactnumber`, `firstname`, `lastname`) VALUES ("'''  + newUserID + '''","''' + username + '''",NULL,NULL,"''' + email + '''","''' + address + '''","''' + emergencyContactName + '''","''' + emergencyContactNumb + '''","''' + firstName + '''","''' + lastName + '''") ''')
            db.connection.commit() # Have to commit the change to the remote database
            cur.close()
            print("Insertion Successful")
            #AWS S3 buckets dont actually use folders or need folders to be made, so its ok to leave creating the folder for 
            #a given user to when they login and upload a profile pic
            #dummy_file = './webapp/static/dummy.txt'
            #upload_file_bucket = 'tm-images-1'
            #upload_file_key = 'users/' + newUserID + '/dummy.txt'
            #uploadCustomImg(dummy_file, upload_file_bucket, upload_file_key)
        else:
            print("Form failed to validate")

    return render_template('NewUser.html', form = form)

'''
page for editing any information about the user
'''
@app.route('/editProfile', methods=['GET', 'POST'])
def editProfile():
    edit_form = EditUserForm()
    upload_form = UploadForm()
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")

    if upload_form.validate_on_submit():
        if upload_form.file.data is not None:
            filename = secure_filename(upload_form.file.data.filename)
            uploaded_image = './webapp/static/profilePic.jpg'
            upload_form.file.data.save(uploaded_image)
            upload_file_bucket = 'tm-images-1'
            upload_file_key = 'users/' + str(conf.user_id) + '/profilepic.jpg'
            uploadCustomImg(uploaded_image, upload_file_bucket, upload_file_key)
            print(filename)

    if upload_form.validate_on_submit(): #works when upload_form.validate but not when edit_form?
        if edit_form.changeUsername.data != '':
            updateUserTable('username',edit_form.changeUsername.data)
        if edit_form.changeEmail.data != '':   
            updateUserTable('email',edit_form.changeEmail.data)
        if edit_form.changePassword.data != '':
            if edit_form.changePassword.data != edit_form.confirmChangePassword.data :
                print("Passwords Don't Match")
            else :
                changePassword(edit_form.changePassword.data,
                               edit_form.confirmChangePassword.data)
        if edit_form.changeDoctorName.data != '':
            updateUserTable('doctor', edit_form.changeDoctorName.data)
        if edit_form.changeDoctorNumber.data != '':
            updateUserTable('doctornumber', edit_form.changeDoctorNumber.data)
        if edit_form.modifyMedications.data != '':
            modifyMedications(edit_form.modifyMedications.data)
        if edit_form.changeEmergencyContactName.data != '':
            updateUserTable('emergencycontact', edit_form.changeEmergencyContactName.data)
        if edit_form.changeEmergencyContactNumb.data != '':
            updateUserTable('emergencycontactnumber', edit_form.changeEmergencyContactNumb.data)
        if edit_form.changeAddress.data != '':
            updateUserTable('address', edit_form.changeAddress.data)

    
    return render_template('EditProfile.html', form_edit = edit_form, form_upload = upload_form, time = nowTime)

'''
page for viewing all the times medicine has been dispensed for patients
'''
@app.route('/dataDashboard', methods=['GET', 'POST'])
def dataDashboard():
    print('Data Dashboard')
    cur = db.connection.cursor()
    cur.execute('''SELECT `user_id` FROM `Users` ORDER BY `user_id` DESC''')
    numbTuple = cur.fetchall()[0]
    numb = numbTuple['user_id']
    print(str(numb))
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")

    cur.execute('''SELECT * FROM `Dispense` WHERE 1 ORDER BY `dispense_time` DESC''')
    log = cur.fetchall()
    length = len(log)
    list=()
    for i in range(length):
        instance = log[i]
        user_id = instance['user_id']
        time = instance['dispense_time']
        cur.execute('''SELECT * FROM `Users` WHERE `user_id` =''' + str(user_id) + '''''')
        results = cur.fetchone()
        username = results['username']
        email = results['email']
        lastName = results['lastname']
        firstName = results['firstname'] 
        row = (user_id, username, email, lastName, firstName, time)
        list = list + (row,)
    print(list)
    headings = ("User_ID", "Username", "Email", "Last Name", "First Name", "Last Dispense Time")
    return render_template('DataDashboard.html', headings=headings, data=list, time=nowTime)

'''
page for viewing media videos, such as tiktoks or youtube videos
'''
@app.route('/media', methods=['GET', 'POST'])
def media():
    cite = "https://www.tiktok.com/@jugglinjosh/video/6955651300449094917"
    videoId = "6955651300449094917"


    return render_template('media.html', cite=cite, videoId = videoId)

@app.route('/multiAdminPortal', methods=['GET', 'POST'])
def multiAdminPortal():
    cur = db.connection.cursor()

    cur.execute('''SELECT `user_id`, `firstname`, `lastname`, `adherence` FROM `Users` WHERE 1''')
    results = cur.fetchall()
    length = len(results)
    list = () 
    for i in range(length):
        instance = results[i]
        lastName = instance['lastname']
        name = {'lastName' : instance['lastname'], 'firstName' : instance['firstname'], 'user_id' : instance['user_id']}
        firstName = instance['firstname']
        adherence = instance['adherence']
        row = (name, adherence)
        list = list + (row,)

    return render_template('multiUserAdminPortal.html', list=list)

'''
page for looking at current, adding, and removing medications
'''
@app.route('/adminPortal/<user_id>', methods=['GET', 'POST'])
def adminPortal(user_id):
    print('Admin Portal')
    med_form = MedicineForm()
    call_form = CallForm()
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")

    cur = db.connection.cursor()

    cur.execute('''SELECT * FROM `Users` WHERE `user_id` = '''+ str(user_id) +'''''')
    names = cur.fetchone()
    firstName = names['firstname']
    print(user_id)
    print("User ID is " + user_id)
    print(firstName)
    lastName = names['lastname']
    if names['AvatarFace'] is None:
        avatar = 'Amy'
    else :
        avatar = names['AvatarFace']
    username = names['username']
    email = names['email']
    address = names['address']
    emergencycontact = names['emergencycontact']
    emergencycontactnumber = names['emergencycontactnumber']
    patientNotes = names['notes']
    patientNotes = patientNotes.replace("\r\n", " <br> ")
    cur.execute('''SELECT * FROM `Prescriptions` WHERE `user_id` =''' + str(user_id))
    results = cur.fetchall()
    length=len(results)
    list=()
    try:
        s3.download_file('tm-images-1', 'users/'+str(user_id)+'/profilepic.jpg', 'webapp/static/profilePic.jpg')
        print("Successfully Downloaded User's Image")
    except: 
        s3.download_file('tm-images-1', 'users/dummyUser/face.jpg', 'webapp/static/profilePic.jpg')
        print("Image Download Failed")
        

    for i in range(length):
        instance=results[i]
        id = instance['id']
        medName = instance['drug']
        dosage = instance['dose']
        frequency = instance['frequency']
        notesRaw = instance['notes']
        notes = notesRaw.replace("\r\n", " <br> ")
        print(instance['times'])
        medImage(medName)
        if instance['times'] == "":
            if frequency == 1 or frequency == "1":
                times = "9 am"
            elif frequency == 2 or frequency == "2":
                times = "9 am; 8 pm"
            elif frequency == 3 or frequency == "3":
                times = "6 am; 12 pm; 6 pm"
            else:
                times = ""
            
               
        else:
            times = instance['times']
        row = (medName, dosage, frequency, times, notes, id)
        print(row)
        list = list + (row,)
    headings = ("Medication Name", "Dosage(mg)", "Daily Frequency", "Times", "Notes")

    if med_form.validate_on_submit() and med_form.medSubmit.data:
        print('Uploading New Med')
        cur.execute('''INSERT INTO `Prescriptions`(`user_id`, `drug`, `dose`, `frequency`, `times`, `notes`) VALUES ('''+str(user_id)+''',"'''+med_form.medicine.data+'''","'''+str(med_form.dosage.data)+'''","'''+str(med_form.frequency.data)+'''","'''+med_form.times.data+'''","'''+med_form.notes.data+'''")''')
        db.connection.commit() # Have to commit the change to the remote database
        cur.close()
        flash(f'Medication {med_form.medicine.data} submitted Successfully.', 'success')
        time.sleep(3)
        return redirect(url_for('adminPortal'))

    
    return render_template('adminPortal.html', med_form=med_form, call_form=call_form, headings=headings, data=list, time=nowTime, username=username, firstName=firstName, lastName=lastName, avatar=avatar, email=email, address=address, emergCont=emergencycontact, emergNumb=emergencycontactnumber, notes=patientNotes)

'''
helper route for refreshing the avatar image
'''
@app.route('/hello', methods=['GET', 'POST'])
def hello():

    # POST request
    if request.method == 'POST' and request.get_json() == 'Custom':
        print('Incoming Custom..')
        print(request.get_json())  # Parse as JSON
        #changeAvatarName(request.get_json())
        updateUserTable('AvatarFace', request.get_json())
        return 'OK', 200 
    else:
        print('Incoming..')
        print(request.get_json())  # Parse as JSON
        #changeAvatarName(request.get_json())
        updateUserTable('AvatarFace', request.get_json())
        return 'OK', 200 

@app.route('/deleteMed', methods=['GET', 'POST'])
def deleteMed():
    cur = db.connection.cursor()

    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # Parse as JSON
        cur.execute('''DELETE FROM `Prescriptions` WHERE `id` = ''' + request.get_json())
        db.connection.commit() # Have to commit the change to the remote database
        cur.close()
        return 'OK', 200

'''
page for whenever pills have been dispensed for the current user
'''
@app.route('/dispenseTime', methods=['GET', 'POST'])  
def dispenseTime():
    now = datetime.now()
    #fulldate = now.strftime("%D %X")
    cur = db.connection.cursor()
    print("Pills Have Been Dispensed")
    print(str(now))
    cur.execute('''INSERT INTO `Dispense`(`user_id`, `dispense_time`) VALUES ('''+ str(conf.user_id) + ''',"''' + str(now) + '''")''')
    db.connection.commit() # Have to commit the change to the remote database
    cur.close()

    return render_template('sandbox.html')

'''
helper route for when the user is recieving a call from their doctor
'''
@app.route('/calling', methods=['GET', 'POST'])
def calling():
    cur = db.connection.cursor()
    print('Calling')
    cur.execute('''UPDATE `Users` SET `zoom` = 1 WHERE `user_id` = ''' + str(conf.user_id))
    db.connection.commit()
    name = getStringUserTable('firstname')
    print(name)
    url = 'https://meet.jit.si/' + name
    webbrowser.open_new_tab(url)
    time.sleep(30)
    cur.execute('''UPDATE `Users` SET `zoom` = 0 WHERE `user_id` = ''' + str(conf.user_id))
    db.connection.commit()
    cur.close()
    return redirect('/adminPortal')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    loadTime = "02:29:30" #Define what the desired loadTime is. Eventually this will be determined by variables in the database
    dayTime = datetime.now()
    nowTime = dayTime.strftime("%X, %Y")
    return (render_template('demo.html', loadTime=loadTime, time=nowTime))

########### Pill Dispenser Section ###########

dispenser = PillDispenser() # Creates a new pill dispenser object

'''
the template for the pill dispensing page
'''
def dispenseTemplate(title="Home Page", text="Default"):
    header = "Dispenser demo. {} packets are ready to go.".format(str(dispenser.getNumPackets()))
    t = datetime.now()
    t = t.strftime("%X, %Y")
    if dispenser.getNumPackets():
        times = dispenser.nextdispense.strftime("%H:%M %p")
    else:
        times = "No packet scanned"
    templateData = {'title': title, 'header': header, 'text': text, 'time': t, 'curtime': t, 'nextime': times}
    return templateData

'''
page for dispensing the pills and viewing the data
'''
@app.route('/dispense')
def dispense():
    text = "Main page"
    templateData = dispenseTemplate(text=text)
    if dispenser.getNumPackets() < dispenser.fullqueuethresh:
        print("need to scan more")
    else:
        #START NEW THREAD TO DISPENSE
        dispenser.dispenseWhenReady()

    return render_template('home.html', **templateData)


########### BUTTONS ###########

'''
route for preparing the first packet
'''
@app.route('/fillDeque')
def runDispenser():
    if dispenser.getNumPackets() < dispenser.fullqueuethresh:
        dispenser.analyzeNextPacket("easyVit")
        t = dispenseTemplate(text="Got data from (1) packets")
    else:
        t = dispenseTemplate(text="Already have (1) packets in the queue! Dispense first!")
    return render_template('home.html', **t)

'''
route for viewing the information from the packet
'''
@app.route('/printPacketInfo')
def printPacketInfo():
    if dispenser.getNumPackets() > 0:
        info = dispenser.peekFirstPacket()
        print(info)
        t = dispenseTemplate(text=info)
    else:
        t = dispenseTemplate(text = "No packets have been scanned!")
    return render_template('home.html', **t)

'''
route for dispensing the packet after it has been analyzed
'''
@app.route('/dispensePacket')
def dispensePacket():
    if dispenser.getNumPackets() > 0:
        packet = dispenser.getFirstPacket()
        t = dispenseTemplate(text = "Dispensing packet " + str(packet.id))
        dispenser.dispenseNextPacket("easyVit")
        dispenser.cutPack()
    else:
        t = dispenseTemplate(text="Can't dispense! No packets have been scanned.")
    return render_template('home.html', **t)

@app.route('/viewNextPacket', methods=['GET','POST'])
def viewNextPacket():
    if request.method == 'POST':
        print(request.get_json())  # Parse as JSON
        shutil.copy(r'/home/pi/MySQLApp/webapp/static/nextNextDose.jpg', r'/home/pi/MySQLApp/webapp/static/nextDose.jpg')
        dispenser.analyzeNextPacket("nurish")
        shutil.copy(r'/home/pi/MySQLApp/webapp/static/pillPic.jpg', r'/home/pi/MySQLApp/webapp/static/nextNextDose.jpg')
        return 'OK', 200

@app.route('/dispenseDemo', methods=['GET','POST'])
def dispenseDemo():

    scheduledDispenseTime = getStringUserTable('scheduled_dispense_time')

    if request.method == 'POST' and request.get_json() == 'Dispense': 
        now = datetime.now()
        cur = db.connection.cursor()
        print("Pills Have Been Dispensed")
        print(str(now))
        adherence = request.get_json()
        print(adherence)
        cur.execute('''INSERT INTO `Dispense`(`user_id`, `dispense_time`, `scheduled_time`, `adherence`) VALUES ('''+ str(conf.user_id) + ''',"''' + str(now) + '''","''' + str(scheduledDispenseTime) +'''","''' + str(adherence) +'''")''')
        db.connection.commit() # Have to commit the change to the remote database
        cur.close() # Close the connection to the sql database
        dispenser.dispenseNextPacket("nurish")
        return 'OK', 200
    elif request.method == 'POST':
        now = datetime.now()
        cur = db.connection.cursor()
        print("Not Dispensing")
        adherence = request.get_json()
        print("reason is:" + adherence)
        cur.execute('''INSERT INTO `Dispense`(`user_id`, `dispense_time`, `scheduled_time`, `adherence`) VALUES ('''+ str(conf.user_id) + ''',"''' + str(now) + '''","''' + str(scheduledDispenseTime) +'''","''' + str(adherence) +'''")''')
        db.connection.commit() # Have to commit the change to the remote database
        cur.close() # Close the connection to the sql database
        return 'OK', 200

@app.route('/record', methods=['GET','POST'])
def record():
    if request.method == 'POST':
        print(request.get_json())

        #VideoStream was used to record the video because it would always use the correct webcam
        #However VideoStream was only working once and then needed python to be rebooted. 
        #So we are using CV2 for now. 
        #webcam = VideoStream(src=0, usePiCamera=False, resolution=(640,480), framerate=25).start()
        webcam = cv2.VideoCapture(0) 
        time.sleep(2.0)
        pins.servoUp()
        video = VideoWriter('webcam.mp4', VideoWriter_fourcc(*'avc1'), 25.0, (640,480))
        for i in range(0,750):
            #frame = webcam.read()
            stream_ok, frame = webcam.read()
            if stream_ok:
                video.write(frame)
                print('Printing Frame' + str(i) )
                time.sleep(0.04)
        time.sleep(3) 
        cv2.destroyAllWindows()
        video.release()
        shutil.copy(r'/home/pi/MySQLApp/webcam.mp4', r'/home/pi/MySQLApp/webapp/static/webcam.mp4')
        pins.servoDown()
        dayTime = datetime.now() # Get the time to create a unqiue code to append to the video
        nowTime = dayTime.strftime("%X, %Y")
        uploaded_image = './webapp/static/webcam.mp4' # Create the route for the new avatar image to go
        upload_file_bucket = 'tm-images-1' # Define the bucket on AWS that will be uploaded to
        upload_file_key = 'users/' + str(conf.user_id) + '/medicationvideos/' + nowTime + '.mp4'  # Define the route on the AWS server that the image will be uploaded to
        uploadCustomImg(uploaded_image, upload_file_bucket, upload_file_key) # Upload the image to the AWS server
        return 'OK', 200

'''
helper route for lowering the blade if it gets stuck up
'''
@app.route('/lowerServo')
def lowerServo():
    pins.servoDown()
    t=dispenseTemplate(text ="Lowering Blade.")
    return render_template('home.html', **t)

'''
helper route for turning the lights on for testing
'''
@app.route('/lightsOn')
def lightsOn():
    pins.backlight_on()
    t=dispenseTemplate(text ="Lighting Lights.")
    return render_template('home.html', **t)

'''
route for taking multiple pictures to aid in training models for new packs
'''
@app.route('/pictureTakin')
def pictureTakin():
    pins.backlight_on()
    for x in range(0,100): # For 100 photos
        numb = str(x)
        t=dispenseTemplate(text = "Taking Picture Number " + numb)
        print('raspistill -o ~/Pictures/EasyVitamin/nurish1_' + numb + '.jpg -vf')
        os.system('raspistill -o ~/Pictures/EasyVitamin/nurish1_' + numb + '.jpg -vf') # Take a photo of the pill pack
        pins.step_motor(1, 800, .004) # Dispense the pill pack a bit to get a different photo
    return render_template('home.html', **t)

'''
helper route for checking if there is a call coming in for the user
'''
@app.route('/checkCall', methods=['GET', 'POST'])
def checkCall():
    # POST request
    if request.method == 'POST':
        print('Checking for a Call')
        recieveCall()
        return 'OK', 200

'''
testing route for anything that needs testing during development
'''
@app.route('/testing')
def sandbox():
    return render_template('sandbox.html')