# An Outreach Bot for [Eventbrite](eventbrite.com)

### Hosted on heroku using heroku buildpacks

## Getting started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

1. Install requirements.txt. I used `pip` to install the packages in the file.

`pip install -r requirements.txt`

2. Selenium requires a driver to interface with the chosen browser. Make sure the driver is in your path, you will need to add your `CHROMEDRIVER_PATH` to the `.env` file.

I used the Chrome driver, you can download it [here](https://sites.google.com/chromium.org/driver/). You can also download [Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/), [Firefox](https://github.com/mozilla/geckodriver/releases) or [Safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10/). Depends on your preferred browser.

### Usage

Fork and clone/download the repository and change the configuration file with:

* Your slack api key
* Run locally, by commenting out the settings for chromedriver executable path, replace with yours.