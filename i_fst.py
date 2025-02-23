from widget import func, ikukuru
import time

def ikukuru_fst(user_data, headless):
  while True:
    for i in user_data:
      driver, wait = func.get_driver(headless)
      ikukuru.login(driver, wait, i["login_mail_address"], i["password"])
      ikukuru.set_search_filter(driver, wait)
      ikukuru.send_fst_message(driver, wait, i["fst_message"], i["name"],15)
      driver.quit()
      time.sleep(2)

if __name__ == '__main__':
  user_data = func.get_user_data()
  headless = True
  ikukuru_fst(user_data["ikukuru"], headless)