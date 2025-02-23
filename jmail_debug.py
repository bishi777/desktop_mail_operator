import jmail_checkmail_fst
from widget import func
import signal
import sys

def signal_handler(signum, frame):
    print("SIGINT")
    sys.exit()

if __name__ == '__main__':
  user_data = func.get_user_data()
  headless = False
  jmail_checkmail_fst.check_mail(user_data, headless)