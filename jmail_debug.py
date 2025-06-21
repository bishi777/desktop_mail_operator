from widget import func, jmail
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
import time

user_data = func.get_user_data()
wait_time = 1.5
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_datas = user_data["jmail"]
base_path = "chrome_profiles/j_footprint"

def jmail_debug(headless):
  user_data = func.get_user_data()
  jmail_datas = user_data["jmail"]

  drivers = jmail.start_jmail_drivers(jmail_datas, headless, base_path)
  while True:
    if drivers == {}:
      break
    for name, data in drivers.items():
      print(name)
      print(data)
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      jmail.check_mail(name,data)
    time.sleep(100)



if __name__ == '__main__':
  
  headless = False
  jmail_debug(headless)
