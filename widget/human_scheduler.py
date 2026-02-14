import random
from datetime import datetime, time, timedelta

class HumanScheduler:
    def __init__(self):
        self.today = datetime.now().date()
        self._set_daily_schedule()
        self.next_break_start = datetime.now() + timedelta(minutes=random.randint(45, 90))
        self.break_end_time = None
        self.is_on_break = False

    def _set_daily_schedule(self):
        """Sets wake and sleep times for the current day."""
        self.wake_time = self._get_random_time(6, 9)  # 06:00 - 09:00
        # Sleep time is for TILL the next morning, so if it's 23:00, it's 23:00 TODAY.
        # If it's 01:00, it's 01:00 TOMORROW.
        self.sleep_hour = random.randint(23, 26) # 23 to 02
        self.sleep_time_is_tomorrow = self.sleep_hour >= 24
        if self.sleep_time_is_tomorrow:
            self.sleep_hour -= 24
        self.sleep_minute = random.randint(0, 59)
        self.today = datetime.now().date()
        print(f"📅 New Schedule for {self.today}: Wake {self.wake_time}, Sleep {self.sleep_hour:02}:{self.sleep_minute:02}")

    def _get_random_time(self, start_hour, end_hour):
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        return time(hour, minute)

    def is_active(self):
        now = datetime.now()
        
        # 0. Check if it's a new day to reset schedule
        if now.date() > self.today:
             # Only reset if we are past the wake up time of the new day to avoid resetting while still sleeping from previous night
             # Actually, simpler: reset if it's morning (e.g. 5AM)
             if now.hour >= 5:
                 self._set_daily_schedule()

        # 1. Sleep/Wake Logic
        current_minutes = now.hour * 60 + now.minute
        wake_minutes = self.wake_time.hour * 60 + self.wake_time.minute
        sleep_minutes = self.sleep_hour * 60 + self.sleep_minute
        
        if self.sleep_time_is_tomorrow:
             sleep_minutes += 24 * 60

        # Logic: Are we in the "awake" window?
        # The awake window starts at wake_time and ends at sleep_time.
        # We need to handle the wrap-around if sleep is tomorrow.
        
        # Current time needs to be adjusted if it's past midnight and before wake time (belonging to previous day's cycle)
        # But simply: 
        # If now is 01:00 and wake is 07:00, we are sleeping.
        # If now is 23:30 and sleep is 23:00, we are sleeping.
        
        # Let's normalize everything to "minutes from wake time TODAY"
        # This is getting complicated. Let's use simple hour checks.
        
        is_sleeping = False
        
        # Case A: Sleep is today (e.g. 23:30)
        # Awake is Wake(07:00) <= Now < Sleep(23:30)
        if not self.sleep_time_is_tomorrow:
             if not (wake_minutes <= current_minutes < sleep_minutes):
                  is_sleeping = True
        
        # Case B: Sleep is tomorrow (e.g. 01:30)
        # Awake is Wake(07:00) <= Now ... (midnight) ... < Sleep(01:30)
        # So inactive if: Sleep(01:30) <= Now < Wake(07:00)
        else:
             # Current time 00:00 - 01:30 -> Awake (late night)
             # Current time 01:30 - 07:00 -> Sleeping
             # Current time 07:00 - 23:59 -> Awake
             
             # If now is early morning (00:00 - Wake)
             if current_minutes < wake_minutes:
                  # If now is after sleep time (01:30 - 07:00) -> Sleep
                  # If now is before sleep time (00:00 - 01:30) -> Awake
                  if current_minutes >= (self.sleep_hour * 60 + self.sleep_minute):
                       is_sleeping = True
             # If now is daytime (Wake - 23:59) -> Awake
             else:
                  pass # Awake

        if is_sleeping:
             # print(f"💤 Sleeping... (Wake at {self.wake_time})")
             return False

        # 2. Break Logic
        if self.is_on_break:
             if now >= self.break_end_time:
                  print("💪 Back to work from break.")
                  self.is_on_break = False
                  # Schedule next break
                  self.next_break_start = now + timedelta(minutes=random.randint(45, 90))
             else:
                  # print(f"☕ On break until {self.break_end_time.strftime('%H:%M')}")
                  return False
        
        elif now >= self.next_break_start:
             duration = random.randint(10, 20)
             if random.random() < 0.1: # 10% chance of long break
                  duration = random.randint(60, 120) 
             
             self.break_end_time = now + timedelta(minutes=duration)
             self.is_on_break = True
             print(f"☕ Taking a break for {duration} min until {self.break_end_time.strftime('%H:%M')}")
             return False

        return True

    def get_sleep_duration(self):
        now = datetime.now()
        if 20 <= now.hour <= 23: # Prime time
             return random.uniform(620, 840)
        elif 8 <= now.hour <= 9 or 12 <= now.hour <= 13: # Commute/Lunch
             return random.uniform(640, 800)
        else:
             return random.uniform(700, 840)

