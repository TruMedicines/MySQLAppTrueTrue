import Algorithmia #imports Algorithmia *duh*
import shutil, os, time #imports shutil(file control commands), os(directory commands), time(keeps track of time)
from webapp import s3, conf

# Handles all avatar creation
# Uses algorithmia (where the code is hosted)

class AvatarCreator():
    #self refers to the class that self is in, so self in this refers to the Avatar Creator Class
    def __init__(self, creds_path="data://trumedicines_rd/Credentials/credentials_json", 
                character="Amy", 
                speech_path="data://trumedicines_rd/VoiceAudio/speech.wav", #speech path Url
                access='simWYqq0UImyQJvwRFmrXPJ72/t1',
                output="data://trumedicines_rd/AvatarVideos/result.mp4"):
        self.creds_path = creds_path #aws credentials on algorithmia
        self.character = character #avatar name
        self.voice = "Amy" #aws voice options: Matthew(male voice), Amy(female voice)
        self.speech_path = speech_path #on algorithmia
        self.client = Algorithmia.client(access) #access to algorithmia
        self.final_output = output #location on algorithmia
        self.prev_location = 'hi.mp4' #local location (so it can be deleted)
        self.custom_face = True #whether the avatar face is user provided or not

    # Runs the entire avatar creation pipeline
    def run(self, text):
        if self.custom_face: #user provided face
            print("custom face")
            #self.downloadCustomAvatar(conf.user_id)
            #self.uploadCustomAvatar()
            self.fullPipeline(text)
        else: #one of our default faces
            self.textToSpeech(text)
            self.lipSync()

    # Runs text to speech on algorithmia
    def textToSpeech(self, text):
        input1 = {
            "creds": self.creds_path,
            "text": text,
            "output": self.speech_path,
            "voice": self.voice
            }

        algo = self.client.algo('trumedicines_rd/TextToSpeech/1.0.4')
        algo.set_options(timeout=300) # optional
        print(algo.pipe(input1).result)

    # Runs lipsync on algorithmia
    def lipSync(self):
        vid = "data://trumedicines_rd/Drivers/" + self.character.lower() + "1.mp4"

        input1 = { #This is a dictionary? Uses key : value format. So video is the value vid so on so on. 
            "video": vid,
            "audio": self.speech_path, #speech path was defined in __init__
            "output": self.final_output #final output was defined in __init__. 
            }

        algo = self.client.algo('trumedicines_rd/LipSync/1.0.0')
        algo.set_options(timeout=300) # optional
        algo.pipe(input1)
        print("lipsync complete. saved at {}".format(self.final_output))

    # Runs the full creation on algorithmia
    def fullPipeline(self, text):
        print('pipeline has begun')
        input = {
            "text": text,
            "image": "data://trumedicines_rd/Faces/amy2.png",
            "voice": self.voice,
            "model": "nongan"
            }
        print('Define Algorithm')
        algo = self.client.algo('trumedicines_rd/CreateTalkingAvatar_WiFi/1.0.1')
        print('Set timeout')
        algo.set_options(timeout=300) # optional
        try:
            print('Begining Generation')
            algo.pipe(input)
            self.final_output = 'data://.algo/trumedicines_rd/LipSync/temp/result.mp4'
            print('Generation Complete')
        except:
            print("Algorithm failed. Try again.")

    # Downloads the avatar vid from algorithmia to the local filename 'output'
    def downloadResult(self, output):
        name = self.getResultFile(self.final_output, output)
        os.remove(name)

    # Helper function to download the avatar vid
    def getResultFile(self, file, output):
        file = self.client.file(file).getFile()
        name = file.name
        shutil.copyfile(name, output) #copies from name to output
        return name

    # Deletes the previous avatar vid, creates the new one, and downloads it
    def updateAvatarVid(self, text):
        if self.prev_location != 'hi.mp4': 
            os.remove(self.prev_location)
        t = time.strftime("%Y%m%d-%H%M%S")
        location = 'webapp/static/currentResponse' + t + '.mp4'
        self.prev_location = location
        self.run(text) # calls 'run' (above)
        self.downloadResult(location)
        return location.split('/')[-1]

    # Downloads the user's custom avatar face from AWS s3
    def downloadCustomAvatar(self, user):
        print("download custom avatar for", user)
        print('users/'+str(user)+'/custom_avatar.jpg')
        s3.download_file('tm-images-1', 'users/'+str(user)+'/custom_avatar.png', 'webapp/static/custom_avatar.png')
        #s3.download_file('tm-images-1', 'test_images/aardvark.jpg', 'test.jpg')

    # Uploads the user's avatar face to algorithmia
    def uploadCustomAvatar(self):
        print('uploading avatar to algorthmia')
        self.client.file("data://trumedicines_rd/Faces/current_custom.png").putFile("webapp/static/custom_avatar.png")
        print('avatar uploaded')

