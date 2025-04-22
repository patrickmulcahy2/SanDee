## Install SanDee in ~ directory
cd ~
rm -f -r SanDee
git clone XXXXXXXXXXXX

### Make system run on startup
crontab -e
@reboot sleep 30 && python3 ~/SanDee/run.py


### install other packages
cd ~/SanDee
sudo pip3 install --break-system-packages -r requirements.txt


### Enable I2C
sudo raspi-config
--> Interfaces 
--> Enable

### Wifi auto connect priority



### To kill program started on boot
sudo netstat -tulnp | grep :8000
sudo kill -9 <PID>



###### HARDWARE SETUP INFO ##########

Raspberry PI 4 with XYZ extra hardware

Pin outs:

## PI DIGITAL PINS FOR RELAYS (BCM):
XYZ_PIN = 13
