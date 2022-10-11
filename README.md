# An Outreach Bot for [Eventbrite](eventbrite.com)

### Hosted on ~~heroku using heroku buildpacks~~ GCP Ubuntu VM

## Getting started

These instructions will get you a copy of the project up and running on both your local machine and on a server for development and testing purposes.

# Running on  Cloud
### Upgrade and Update the OS
1. sudo apt update
2. sudo apt upgrade

### Install PIP
1. sudo apt install python3-pip
### Install some dependency packages
1. sudo apt install software-properties-common
2. sudo apt-get install gconf-service libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxss1 libxtst6 libappindicator1 libnss3 libasound2 libatk1.0-0 libc6 ca-certificates fonts-liberation lsb-release xdg-utils wget
### Clone the repo and cd into it
1.  git clone https://github.com/heavenya/email_bot.git
2. cd email_bot
### Install  venv Package
1. sudo apt install python3.10-venv
### Create a virtual environment
1. python3 -m venv venv
### Install packages in requirements file
1. pip install -r requirements.txt
### Download and install Chrome browser
1. wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
2. sudo apt install ./google-chrome-stable_current_amd64.deb
### Export slack ACCESS_TOKEN:
1. export ACCESS_TOKEN=xoxb-******-*******-********
### Upgrade Jellyfist package duw to this issue: https://github.com/unitedstates/python-us/issues/65
1. pip install -Iv jellyfish
### Run as a background service using nohup
1. nohup python main.py > test2.log &
2. ps -fA | grep python


# Running on Local

### Prerequisites

1. Install requirements.txt. I used `pip` to install the packages in the file.

`pip install -r requirements.txt`

2. Selenium requires a driver to interface with the chosen browser. Make sure the driver is in your path, you will need to add your `CHROMEDRIVER_PATH` to the `.env` file.

I used the Chrome driver, you can download it [here](https://sites.google.com/chromium.org/driver/). You can also download [Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/), [Firefox](https://github.com/mozilla/geckodriver/releases) or [Safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10/). Depends on your preferred browser.

### Usage

Fork and clone/download the repository and change the configuration file with:

* Your slack api key
* Run locally, by commenting out the settings for chromedriver executable path, replace with yours.