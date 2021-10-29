import Algorithmia #imports Algorithmia
import shutil, os, time #imports shutil(file control commands), os(directory commands), time(keeps track of time)
from webapp import s3

class DefaultImages():

    def __init__(self, creds_path="data://trumedicines_rd/Credentials/credentials_json", 
                character="Amy", 
                speech_path="data://trumedicines_rd/VoiceAudio/speech.wav", #speech path Url
                access='simWYqq0UImyQJvwRFmrXPJ72/t1',
                amyImage="data://trumedicines_rd/ExampleAvatarFaces/amy.png",
                frankImage="data://trumedicines_rd/ExampleAvatarFaces/frank.png",
                jackieImage="data://trumedicines_rd/ExampleAvatarFaces/jackie.png",
                kurtImage="data://trumedicines_rd/ExampleAvatarFaces/kurt.png"):
        print("Changing Images")
        self.creds_path = creds_path #aws credentials on algorithmia
        self.character = character #avatar name
        self.client = Algorithmia.client(access) #access to algorithmia
        #self.final_output = output #location on algorithmia
        self.prev_amy = 'webapp/static/Amy.png' #local location (so it can be deleted)
        self.prev_frank = 'webapp/static/Frank.png' #local location (so it can be deleted)
        self.prev_jackie = 'webapp/static/Jackie.png' #local location (so it can be deleted)
        self.prev_kurt = 'webapp/static/Kurt.png' #local location (so it can be deleted)

        self.update(amyImage, frankImage, jackieImage, kurtImage)

    '''
    function for updating the images of the default avatars
    '''
    def update(self, amyImage, frankImage, jackieImage, kurtImage):
        print("deleting old image")
        #delete previous images
        os.remove(self.prev_amy)
        os.remove(self.prev_frank)
        os.remove(self.prev_jackie)
        os.remove(self.prev_kurt)
        #Get the new files from the aws server
        fileAmy = self.client.file(amyImage).getFile()
        fileFrank = self.client.file(frankImage).getFile()
        fileJackie = self.client.file(jackieImage).getFile()
        fileKurt = self.client.file(kurtImage).getFile()
        #defines locations for the new images that will be downloaded
        locationAmy = 'webapp/static/Amy.png'
        locationFrank = 'webapp/static/Frank.png'
        locationJackie = 'webapp/static/Jackie.png'
        locationKurt = 'webapp/static/Kurt.png'
        #copy the images from aws to the local location in static
        shutil.copyfile(fileAmy.name,locationAmy)
        shutil.copyfile(fileFrank.name,locationFrank)
        shutil.copyfile(fileJackie.name,locationJackie)
        shutil.copyfile(fileKurt.name,locationKurt)
