#!/bin/bash
# startup.sh
#Open Chromium on the Raspberry Pi on fullscreen on bootup. Then open the virtual environemnt, and then run our python script


cd /
cd /home/pi/MySQLAppTrueTrue 
sudo /home/pi/.virtualenvs/tm/bin/python /home/pi/MySQLAppTrueTrue/main.py
chromium-browser --start-fullscreen https://www.google.com/
#sudo chromium-browser --start-fullscreen 127.0.0.1:5000
#su - pi -c /usr/bin/chromium-browser --start-fullscreen 127.0.0.1:5000
#su - pi -c "/usr/bin/chromium-browser --start-fullscreen 127.0.0.1:5000"
#source /usr/local/bin/virtualenvwrapper.sh
#source ~/.bashrc
#workon /home/pi/.virtualenvs/tm
#workon tm
#sudo python /home/pi/MySQLAppTrueTrue/main.py
