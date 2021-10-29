## Classes for generic packet and each specific packet type

import cv2
import datetime
import numpy as np

### TODOS
# Make the text gathering more generic
# Figure out a better way to set the dispense time

class Packet():
    def __init__(self):
        self.id = 0
        self.image = None
        self.Pills = []
        self.Barcode = None
        self.complete = False

    def addPill(self, pill):
        self.Pills.append(pill)
        
    def addBarcode(self, Barcode):
        self.Barcode = Barcode

    def setDispenseTime(self):
        if self.timeofday == "morning":
            now = datetime.datetime.now()
            self.dispense_time = now + datetime.timedelta(minutes=2)
        return self.dispense_time



class PersonaPacket(Packet):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.timeofday = 0
        self.vitamin = ""
        self.dispense_time = datetime.time(8,0)  

    def __str__(self):
        return "\n Persona packet info: {} \n  User: {} \n  Vitamin: {} \n  Will dispense at {} \n  Pill: {} pill(s)".format(self.id,
                self.name, self.vitamin, self.dispense_time.strftime("%H:%M %p"), len(self.Pills)
        )

    def addText(self, words):
        for word in words:
            if word:
                word = word.lower().strip()
                if "vitamin" in word:
                    self.vitamin = word
                elif "morning" in word:
                    self.timeofday = "morning"
                elif "charlie" in word:
                    self.name = word

    def setDispenseTime(self):
        if self.timeofday == "morning":
            now = datetime.datetime.now()
            self.dispense_time = now + datetime.timedelta(minutes=4)
        return now + datetime.timedelta(minutes=4)

    def flipWord(self, word):
        word = cv2.flip(word, 1)
        return word


class NurishPacket(Packet):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.timeofday = "morning"
        self.vitamin = "Vitamin B12"
        self.message = ""
        self.expiration = ""
        self.lotnum = ""
        self.dispense_time = datetime.time(8,0)  

    def __str__(self):
        return "\n Nurish packet info: {} \n  User: {} \n  Message: {} \n  Will dispense at {} \n  Expire: {} \n Lot: {}\n".format(
            self.id, self.name, self.message, self.dispense_time.strftime("%H:%M %p"), self.expiration, self.lotnum
        )

    def addText(self, words):
        for word in words:
            if word:
                word = word.lower().strip()
                if "vitamin" in word:
                    self.vitamin = word
                elif "david" in word:
                    self.name = word
                elif "walk" in word or "end" in word:
                    self.message = word
                elif "exp" in word:
                    self.expiration = word
                elif "lot" in word:
                    self.lotnum = word

    

    def flipWord(self, word):
        word = cv2.flip(word, -1)
        word = cv2.flip(word, 1)
        return word

    def flipImage(self, im):
        #im = cv2.flip(im, -1) #-1 flips both over x and y axis
        #im = cv2.flip(im, 1) #1 flips across 7 axis
        im = cv2.flip(im, 0)
        return im

class EasyVitamin(Packet):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.timeofday = "morning"
        self.vitamin = "Vitamin B12"
        self.message = ""
        self.expiration = ""
        self.lotnum = ""
        self.dispense_time = datetime.time(8,0)  

    def __str__(self):
        return "\n EasyVitamin packet info: {} \n  User: {} \n  Message: {} \n  Will dispense at {} \n  Expire: {} \n Lot: {}\n".format(
            self.id, self.name, self.message, self.dispense_time.strftime("%H:%M %p"), self.expiration, self.lotnum
        )

    def addText(self, words):
        for word in words:
            if word:
                word = word.lower().strip()
                if "vitamin" in word:
                    self.vitamin = word
                elif "david" in word:
                    self.name = word
                elif "walk" in word or "end" in word:
                    self.message = word
                elif "exp" in word:
                    self.expiration = word
                elif "lot" in word:
                    self.lotnum = word

    

    def flipWord(self, word):
        word = cv2.flip(word, -1)
        word = cv2.flip(word, 1)
        return word

    def flipImage(self, im):
        im = cv2.flip(im, -1)
        im = cv2.flip(im, 1)
        return im

    

