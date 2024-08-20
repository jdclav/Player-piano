sudo apt-get install -y python3 python3-dev libasound2-dev libasound2-plugins
echo 'pcm.default pulse
ctl.default pulse' > ~/.asoundrc
sudo pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt