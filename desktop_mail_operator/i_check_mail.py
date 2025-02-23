from widget import func, ikukuru
import time

def ikukuru_check_mail(ikukuru_data, gmail_account, gmail_account_password, recieve_mailaddress, headless):
  while True:
    for i in ikukuru_data:
      # if i["name"] == "アスカ":
        
        driver, wait = func.get_driver(headless)
        ikukuru.login(driver, wait, i["login_mail_address"], i["password"])
        ikukuru.check_mail(driver, wait, i, gmail_account, gmail_account_password, recieve_mailaddress)

        driver.quit()
        time.sleep(2)

if __name__ == '__main__':
  user_data = func.get_user_data()
  headless = True
  print(user_data["user"] )

  gmail_account = user_data["user"][0]["gmail_account"]
  gmail_account_password = user_data["user"][0]["gmail_account_password"]
  recieve_mailaddress =  user_data["user"][0]["user_email"]

  ikukuru_check_mail(user_data["ikukuru"], gmail_account, gmail_account_password, recieve_mailaddress, headless)