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
        """Sets wake and sleep times for the current day.
        偶数日 → Aスケジュール（3枠のみ稼働）
        奇数日 → Bスケジュール（従来の通常スケジュール）
        """
        self.today = datetime.now().date()

        # 偶数日 → Aスケジュール（3枠のみ）、奇数日 → Bスケジュール（通常）
        day_number = self.today.toordinal()
        if day_number % 2 == 0:
            self.schedule_mode = "A"
        else:
            self.schedule_mode = "B"

        if self.schedule_mode == "B":
            # Wake time: 06:00 - 07:30
            total_minutes = random.randint(6 * 60, 7 * 60 + 30)
            wake_hour = total_minutes // 60
            wake_minute = total_minutes % 60
            self.wake_time = time(wake_hour, wake_minute)

            # Sleep time: 23:00 - 00:10 (Next day)
            total_sleep_minutes = random.randint(1380, 1450)
            self.sleep_hour = total_sleep_minutes // 60
            self.sleep_minute = total_sleep_minutes % 60
            self.sleep_time_is_tomorrow = self.sleep_hour >= 24
            if self.sleep_time_is_tomorrow:
                self.sleep_hour -= 24

        else:
            # Aスケジュール：3枠のみ（±5分のランダムゆらぎ）
            # 枠1: 7:10 〜 8:10
            # 枠2: 12:50 〜 14:00
            # 枠3: 20:00 〜 21:00
            def clamp(v, lo, hi):
                return max(lo, min(hi, v))

            self.schedule_windows = [
                (
                    time(7, clamp(10 + random.randint(-5, 5), 0, 59)),
                    time(8, clamp(10 + random.randint(-5, 5), 0, 59)),
                ),
                (
                    time(12, clamp(50 + random.randint(-5, 5), 0, 59)),
                    time(14, clamp( 0 + random.randint(-5, 5), 0, 59)),
                ),
                (
                    time(20, clamp( 0 + random.randint(-5, 5), 0, 59)),
                    time(21, clamp( 0 + random.randint(-5, 5), 0, 59)),
                ),
            ]

        print(f"📅 New Schedule for {self.today}: Mode={self.schedule_mode}", end=" ")
        if self.schedule_mode == "A":
            for w in self.schedule_windows:
                print(f"[{w[0].strftime('%H:%M')}-{w[1].strftime('%H:%M')}]", end=" ")
            print()
        else:
            print(f"Wake {self.wake_time}, Sleep {self.sleep_hour:02}:{self.sleep_minute:02}")

    def _get_random_time(self, start_hour, end_hour):
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        return time(hour, minute)

    def is_active(self):
        now = datetime.now()

        # 0. Check if it's a new day to reset schedule
        if now.date() > self.today:
            if now.hour >= 5:
                self._set_daily_schedule()

        # --- Aスケジュール: 3枠ウィンドウ判定 ---
        if self.schedule_mode == "A":
            current_time = now.time()
            in_window = any(start <= current_time <= end for (start, end) in self.schedule_windows)
            if not in_window:
                return False

        # --- Bスケジュール: 既存の wake/sleep 判定 ---
        else:
            current_minutes = now.hour * 60 + now.minute
            wake_minutes = self.wake_time.hour * 60 + self.wake_time.minute
            sleep_minutes = self.sleep_hour * 60 + self.sleep_minute

            if self.sleep_time_is_tomorrow:
                sleep_minutes += 24 * 60

            is_sleeping = False

            # Case A: Sleep is today (e.g. 23:30)
            if not self.sleep_time_is_tomorrow:
                if not (wake_minutes <= current_minutes < sleep_minutes):
                    is_sleeping = True

            # Case B: Sleep is tomorrow (e.g. 01:30)
            else:
                if current_minutes < wake_minutes:
                    if current_minutes >= (self.sleep_hour * 60 + self.sleep_minute):
                        is_sleeping = True

            if is_sleeping:
                return False

        # 2. Break Logic（両モード共通）
        if self.is_on_break:
            if now >= self.break_end_time:
                print("💪 Back to work from break.")
                self.is_on_break = False
                self.next_break_start = now + timedelta(minutes=random.randint(45, 90))
            else:
                return False

        elif now >= self.next_break_start:
            duration = random.randint(10, 20)
            if random.random() < 0.1:  # 10% chance of long break
                duration = random.randint(60, 120)

            self.break_end_time = now + timedelta(minutes=duration)
            self.is_on_break = True
            print(f"☕ Taking a break for {duration} min until {self.break_end_time.strftime('%H:%M')}")
            return False

        return True

    def get_sleep_duration(self):
        now = datetime.now()
        if 20 <= now.hour <= 23:  # Prime time
            return random.uniform(620, 840)
        elif 8 <= now.hour <= 9 or 12 <= now.hour <= 13:  # Commute/Lunch
            return random.uniform(640, 800)
        else:
            return random.uniform(700, 840)
