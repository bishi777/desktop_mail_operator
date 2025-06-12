from widget import func, jmail
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait


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

  login_id = jmail_datas[0]['login_id']
  login_pass = jmail_datas[0]['password']
  drivers = jmail.start_jmail_drivers(login_id, login_pass, jmail_datas, headless, base_path)
  print(drivers)
  # jmail.re_post(driver)



if __name__ == '__main__':
  
  headless = False
  jmail_debug(headless)
