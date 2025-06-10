## Install SanDee in ~ directory
cd ~
rm -f -r SanDee
git clone https://github.com/patrickmulcahy2/SanDee


### Make system run on startup
crontab -e
@reboot sleep 30 && python3 ~/SanDee/run.py


### Set up Virtual Environment
sudo apt update
sudo apt install python3-venv
cd ~
python3 -m venv myenv
source myenv/bin/activate
(to deactivate)
deactivate


### install other packages
cd ~/SanDee
sudo pip3 install --break-system-packages -r requirements.txt


### make ./updateRun.sh shell
cd ~
nano updateRun.sh

Add:
cd ~
nano updateRun.sh
git clone https://github.com/patrickmulcahy2/SanDee

Run:
chmod +x updateRun.sh


### Enable I2C
sudo raspi-config
--> Interfaces 
--> Enable


### Wifi auto connect priority
xyz
xyz
xyz


### To kill program started on boot
sudo netstat -tulnp | grep :8000
sudo kill -9 <PID>



###### HARDWARE SETUP INFO ##########

Raspberry PI 4 with XYZ extra hardware

Pin outs:

## PI DIGITAL PINS FOR RELAYS (BCM):
XYZ_PIN = 13
