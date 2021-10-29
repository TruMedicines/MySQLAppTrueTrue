from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, PasswordField, DateField, FileField, FieldList, DateTimeField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, email_validator

# accepts the text for the avatar to speak and chose the Avatar
class AvatarForm(FlaskForm):
    text = StringField('Speech Text', validators=[DataRequired()])
    submitAvatar = SubmitField('Create Video')

# accepts the image of the custom avatar 
class CustomAvatarForm(FlaskForm):
    file = FileField()
    submitCustom = SubmitField('Upload Custom Avatar')

# accepts the profile image of the user
class UploadForm(FlaskForm):
    file = FileField()

# accepts the username for the user to be logged into
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Submit')

# accepts all the information required to make a profile
class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=2, max=20)])
    #password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    #confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=2, max=20), EqualTo('password')])

    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=40)])
    #birthDate = DateField('Birth Date', validators=[DataRequired()])
    #doctorName = StringField('Doctor Name', validators=[DataRequired(), Length(min=2, max=20)])
    #doctorNumber = StringField('Doctors Phone Number', validators=[DataRequired(), Length(min=10, max=11)])
    #medications = StringField('Medications')
    emergencyContactName = StringField('Emergency Contact Name', validators=[DataRequired(), Length(min=2, max=30)])
    emergencyContactNumb = StringField('Emergency Contact Number', validators=[DataRequired(), Length(min=10, max=11)])

    #customImage = FileField('Custom Image Upload')
    submit = SubmitField('Create Account')

# accepts all the information for editing a profile
class EditUserForm(FlaskForm):
    changeUsername = StringField('Change Username', validators=[Length(min=2, max=20)])
    changeEmail = StringField('Change Email', validators=[Length(min=2, max=20)])

    changePassword = PasswordField('Change Password', validators=[Length(min=2, max=20)])
    confirmChangePassword = PasswordField('Confirm Change Password', validators=[Length(min=2, max=20), EqualTo('changePassword')])

    changeDoctorName = StringField('Change Doctor Name', validators=[Length(min=2, max=20)])
    changeDoctorNumber = StringField('Change Doctors Phone Number', validators=[Length(min=10, max=11)])
    modifyMedications = StringField('Modify Medications')

    changeEmergencyContactName = StringField('Change Emergency Contact Name', validators=[Length(min=2, max=20)])
    changeEmergencyContactNumb = StringField('Change Emergency Contact Number', validators=[Length(min=10, max=11)])
    
    changeAddress = StringField('Change Address', validators=[Length(min=3, max=30)])
    oldPassword = StringField('Previous Password')
    submitChanges = SubmitField('Submit Changes')

# accepts all the information required to add a new medication
class MedicineForm(FlaskForm):
    medicine = StringField('Medication Name')
    dosage = IntegerField('Dosage')
    frequency = IntegerField('Daily Frequency')
    times = StringField('Time')
    notes = TextAreaField('Additional Notes')
    medSubmit = SubmitField('Update Medications')

# creates the button to be pressed by the doctor to call the patient
class CallForm(FlaskForm):
    callSubmit = SubmitField('Call Current Patient')

# Creates a button for the user to confirm that they want to take their medications. 
class MedConfForm(FlaskForm):
    submit = SubmitField('Yes')