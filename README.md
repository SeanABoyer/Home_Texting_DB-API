# Home_Texting_DB-API
A DataBase/API for the Desktop and Mobile Home Texting Apps

## How to install on raspberryPi
	-SSH to raspberryPi
	-mkdir /usr/local/bin/HomeTextService && cd /usr/local/bin/HomeTextService
	-wget https://github.com/SeanABoyer/Home_Texting_DB-API/archive/master.zip
	-unzip -j master.zip
	-apt-get install virtualenv
	-virtualenv -p /usr/bin/python3 py3env
	-source py3env/bin/activate
	-pip install -r requirements.txt
	-sudo mv HomeTextService.sh /etc/init.d
	-sudo chmod 755 /etc/init.d/HomeTextService.sh

