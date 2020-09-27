sudo rm -r /home/pi/Max_Core_RELEASE
sudo cp -r /home/pi/backup/Max_Core_RELEASE /home/pi
cd /home/pi/Max_Core_RELEASE
sudo python3 /home/pi/Max_Core_RELEASE/Core.py > /home/pi/output.log
