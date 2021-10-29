from flask import Flask, render_template, send_file
from PillDispenser import PillDispenser
from datetime import datetime
import cv2

'''
Flask app for testing the dispenser functions: scanning, dispensing.
'''

app = Flask(__name__)

dispenser = PillDispenser()

def template(title="Home Page", text="Default"):
    header = "Dispenser demo. {} packets are ready to go.".format(str(dispenser.getNumPackets()))
    t = datetime.now()
    t = t.strftime("%X, %Y")
    if dispenser.getNumPackets():
        times = dispenser.nextdispense.strftime("%H:%M %p")
    else:
        times = "No packet scanned"
    templateData = {'title': title, 'header': header, 'text': text, 'time': t, 'curtime': t, 'nextime': times}
    return templateData

@app.route('/')
def home():
    text = "Main page"
    templateData = template(text=text)
    if dispenser.getNumPackets() < dispenser.fullqueuethresh:
        print("need to scan more")
    else:
        #START NEW THREAD TO DISPENSE
        dispenser.dispenseWhenReady()

    return render_template('home.html', **templateData)


#### BUTTONS ####

@app.route('/fillDeque')
def runDispenser():
    if dispenser.getNumPackets() < dispenser.fullqueuethresh:
        dispenser.analyzeNextPacket()
        t = template(text="Got data from (1) packets")
    else:
        t = template(text="Already have (1) packets in the queue! Dispense first!")
    return render_template('home.html', **t)

@app.route('/printPacketInfo')
def printPacketInfo():
    if dispenser.getNumPackets() > 0:
        info = dispenser.peekFirstPacket()
        print(info)
        t = template(text=info)
    else:
        t = template(text = "No packets have been scanned!")
    return render_template('home.html', **t)

@app.route('/dispensePacket')
def dispensePacket():
    if dispenser.getNumPackets() > 0:
        packet = dispenser.getFirstPacket()
        t = template(text = "Dispensing packet " + str(packet.id))
        dispenser.dispenseNextPacket()
    else:
        t = template(text="Can't dispense! No packets have been scanned.")
    return render_template('home.html', **t)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')


