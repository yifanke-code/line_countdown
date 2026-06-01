#!/usr/bin/env python3
import sys
import argparse
import threading
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# LINE recipients configuration (user_id: display_name)
LINE_RECIPIENTS = {
    "U62f156ab5afd221576ea85039ac4ed21": "Evan",
    "U40c729ba870837553332a7179e97f854": "Cheryl",
    "Ca1234567890abcdef1234567890abc": "Group Chat 1",
}

# Timezone abbreviation mapping
TZ_MAP = {
    'CDT': 'America/Chicago',
    'CST': 'America/Chicago',
    'EDT': 'America/New_York',
    'EST': 'America/New_York',
    'PDT': 'America/Los_Angeles',
    'PST': 'America/Los_Angeles',
    'GMT': 'UTC',
    'UTC': 'UTC',
    'JST': 'Asia/Tokyo',
    'IST': 'Asia/Kolkata',
    'SGT': 'Asia/Singapore',
    'HKT': 'Asia/Hong_Kong',
}

class CommandLineCountdown:
    def __init__(self, tz_str, datetime_str, message, user_names):
        self.tz_str = tz_str
        self.datetime_str = datetime_str
        self.message = message or "倒數計時"
        self.user_names = user_names
        self.target_time = None
        self.sent_notifications = set()
        self.running = False

    def parse_timezone(self, tz_str):
        """Parse timezone string (CDT, UTC-3, Asia/Taipei, etc.)"""
        tz_str = tz_str.strip().upper()

        # Check abbreviation mapping
        if tz_str in TZ_MAP:
            return ZoneInfo(TZ_MAP[tz_str])

        # Handle UTC±X format
        if tz_str.startswith('UTC'):
            offset_str = tz_str[3:]
            if offset_str:
                try:
                    offset = int(offset_str)
                    if offset == 0:
                        return ZoneInfo('UTC')
                    # Create a fixed offset timezone
                    from datetime import timezone
                    return timezone(timedelta(hours=offset))
                except:
                    return None
            return ZoneInfo('UTC')

        # Try as IANA timezone
        try:
            return ZoneInfo(tz_str)
        except:
            return None

    def parse_datetime_10digit(self, date_str, tz_info):
        """Parse 10-digit datetime string (YYMMDDHHMI)"""
        date_str = date_str.strip()
        if len(date_str) != 10 or not date_str.isdigit():
            return None

        try:
            yy = int(date_str[0:2])
            mm = int(date_str[2:4])
            dd = int(date_str[4:6])
            hh = int(date_str[6:8])
            mi = int(date_str[8:10])

            # Assume 20YY for 2-digit year
            year = 2000 + yy

            return datetime(year, mm, dd, hh, mi, 0, tzinfo=tz_info)
        except:
            return None

    def get_recipient_ids(self, user_names):
        """Get LINE user IDs from display names"""
        recipient_ids = []
        for name in user_names:
            found = False
            for user_id, display_name in LINE_RECIPIENTS.items():
                if display_name.lower() == name.lower():
                    recipient_ids.append(user_id)
                    found = True
                    break
            if not found:
                print(f"⚠ 警告: 找不到使用者 '{name}'")
        return recipient_ids

    def calculate_notify_times(self):
        """Calculate notification times"""
        # 使用保存的 target_dt（已包含正確的時區信息）
        target_dt = self.target_dt

        # 計算Taipei time (UTC+8)
        taipei_tz = ZoneInfo('Asia/Taipei')
        target_dt_taipei = target_dt.astimezone(taipei_tz)

        # 格式化時區顯示名稱
        tz_display = self.tz_str.upper()
        if tz_display in TZ_MAP:
            # 如果是縮寫，顯示縮寫
            pass
        elif tz_display.startswith('UTC'):
            # 保持 UTC±X 格式
            pass
        else:
            # 對於 IANA timezone，提取最後一部分
            tz_display = tz_display.split('/')[-1]

        times_str = f"⏰ 倒數開始時間\n"
        times_str += f"{target_dt.strftime('%m-%d')} {tz_display}: {target_dt.strftime('%H:%M')}\n"
        times_str += f"{target_dt_taipei.strftime('%m-%d')} Taipei time: {target_dt_taipei.strftime('%H:%M')}"

        return times_str

    def send_line_message(self, user_id, message):
        """Send LINE message in a separate thread"""
        thread = threading.Thread(target=self.send_line_message_thread, args=(user_id, message))
        thread.daemon = True
        thread.start()

    def send_line_message_thread(self, user_id, message):
        """Send LINE message (thread worker)"""
        try:
            from linebot.v3.messaging import (Configuration, ApiClient, MessagingApi,
                                              PushMessageRequest, TextMessage)

            configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=message)]
                    )
                )
            print(f"✓ LINE 訊息已發送給 {user_id}")
        except Exception as e:
            print(f"✗ LINE 發送錯誤: {e}")

    def send_line_to_recipients(self, recipients, message):
        """Send LINE message to multiple recipients"""
        for recipient_id in recipients:
            self.send_line_message(recipient_id, message)

    def validate_inputs(self):
        """Validate and parse all inputs"""
        # Parse timezone
        tz_info = self.parse_timezone(self.tz_str)
        if tz_info is None:
            print(f"✗ 錯誤: 無效的時區 '{self.tz_str}'")
            print("  支援格式: CDT, EST, UTC-3, Asia/Taipei, 等...")
            return False

        # Parse datetime
        target_dt = self.parse_datetime_10digit(self.datetime_str, tz_info)
        if target_dt is None:
            print(f"✗ 錯誤: 無效的日期時間格式 '{self.datetime_str}'")
            print("  正確格式: 10位數 (如: 2605201722 => 2026/05/20 17:22)")
            return False

        self.target_time = int(target_dt.timestamp() * 1000)
        self.target_dt = target_dt

        # Validate recipients
        recipients = self.get_recipient_ids(self.user_names)
        if not recipients:
            print("✗ 錯誤: 沒有有效的接收對象")
            print(f"  可用的使用者: {', '.join([name for _, name in LINE_RECIPIENTS.items()])}")
            return False

        self.recipients = recipients
        return True

    def print_startup_info(self):
        """Print startup information"""
        print("=" * 60)
        print("LINE 倒數計時 - 命令列版本")
        print("=" * 60)
        print(f"時區: {self.tz_str}")
        print(f"目標時間: {self.target_dt.strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"通知主題: {self.message}")
        print(f"接收對象: {', '.join([LINE_RECIPIENTS[r] for r in self.recipients])}")
        print("=" * 60)
        print(self.calculate_notify_times())
        print("=" * 60)

    def format_countdown(self, diff_ms):
        """Format countdown display"""
        if diff_ms >= 0:
            days = diff_ms // (1000 * 60 * 60 * 24)
            hours = (diff_ms % (1000 * 60 * 60 * 24)) // (1000 * 60 * 60)
            minutes = (diff_ms % (1000 * 60 * 60)) // (1000 * 60)
            seconds = (diff_ms % (1000 * 60)) // 1000
            return f"{int(days):02d}天 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            elapsed = -diff_ms
            days = elapsed // (1000 * 60 * 60 * 24)
            hours = (elapsed % (1000 * 60 * 60 * 24)) // (1000 * 60 * 60)
            minutes = (elapsed % (1000 * 60 * 60)) // (1000 * 60)
            seconds = (elapsed % (1000 * 60)) // 1000
            return f"+{int(days):02d}天 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def run(self):
        """Run the countdown loop"""
        if not self.validate_inputs():
            return False

        self.print_startup_info()

        # Send initial notification
        notify_times = self.calculate_notify_times()
        initial_message = f"【預計通知時間】{self.message}\n{notify_times}"
        self.send_line_to_recipients(self.recipients, initial_message)

        self.running = True
        print("\n開始倒數...\n")

        try:
            while self.running:
                now_ms = int(datetime.now().timestamp() * 1000)
                diff = self.target_time - now_ms
                current_time = int(datetime.now().timestamp() * 1000)

                # Handle notifications after target time
                if diff <= 0:
                    elapsed = current_time - self.target_time

                    # Calculate current notification number
                    current_notification_num = int(elapsed / (10 * 60 * 1000)) + 1
                    current_notification_num = min(current_notification_num, 15)

                    # Send notification if not sent yet
                    if current_notification_num not in self.sent_notifications:
                        self.sent_notifications.add(current_notification_num)
                        now_str = datetime.now().strftime("%H:%M:%S")

                        if current_notification_num == 1:
                            msg = f"【時間到】{self.message} (第 1/15 次) ({now_str})"
                        else:
                            msg = f"【提醒】{self.message} (第 {current_notification_num}/15 次) ({now_str})"

                        self.send_line_to_recipients(self.recipients, msg)
                        print(f"[{now_str}] {msg}")

                    # Stop after 15 notifications
                    if current_notification_num >= 15 and 15 in self.sent_notifications:
                        print("\n✓ 倒數完成！已發送全部15次通知")
                        self.running = False
                        break

                # Display countdown
                countdown_display = self.format_countdown(diff)
                status_line = f"\r倒數時間: {countdown_display}"
                sys.stdout.write(status_line)
                sys.stdout.flush()

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⚠ 倒數已中止")
            self.running = False

        return True

def main():
    parser = argparse.ArgumentParser(
        description='LINE 倒數計時 - 命令列版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python countdown_linux.py -tz=CDT -dt=2605201722 -m=Hello -u=Evan
  python countdown_linux.py -tz=UTC+8 -dt=2612312359 -m=New_Year -u=Evan -u=Person_2
  python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -m=Test
        """
    )

    parser.add_argument('-tz', '--timezone', required=True, dest='timezone',
                        help='時區 (如: CDT, EST, UTC+8, Asia/Taipei)')
    parser.add_argument('-dt', '--datetime', required=True, dest='datetime',
                        help='日期時間 (10位數: YYMMDDHHMI, 如: 2605201722)')
    parser.add_argument('-m', '--message', dest='message',
                        help='通知主題 (預設: 倒數計時)')
    parser.add_argument('-u', '--user', dest='users', action='append',
                        help='接收對象 (可重複指定多個使用者)')

    args = parser.parse_args()

    if not args.users:
        print("✗ 錯誤: 必須指定至少一個接收對象 (-u)")
        print(f"  可用的使用者: {', '.join([name for _, name in LINE_RECIPIENTS.items()])}")
        sys.exit(1)

    countdown = CommandLineCountdown(
        tz_str=args.timezone,
        datetime_str=args.datetime,
        message=args.message,
        user_names=args.users
    )

    success = countdown.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
