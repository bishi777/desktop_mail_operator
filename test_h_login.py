import time
from widget import happymail, func, pcmax
from DrissionPage import ChromiumPage

user_data = func.get_user_data()["happymail"][4]
driver,wait = func.test_get_driver(None, False)
wait_time = 1.5
name = user_data["name"]
login_id = user_data["login_id"]
login_pass = user_data["password"]

happymail.login(name, login_id, login_pass, driver, wait,)