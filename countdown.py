import sys
import urllib.parse
import threading
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QLineEdit, QHBoxLayout, QComboBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import QTimer, QDateTime, QDate
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

TIMEZONES = {
    # UTC-12 至 UTC-8
    "斐濟 (UTC+12)": "Pacific/Fiji",
    "紐西蘭 (UTC+12)": "Pacific/Auckland",
    "雪梨 (UTC+10)": "Australia/Sydney",
    "東京 (UTC+9)": "Asia/Tokyo",
    "首爾 (UTC+9)": "Asia/Seoul",
    "香港 (UTC+8)": "Asia/Hong_Kong",
    "台北 (UTC+8)": "Asia/Taipei",
    "新加坡 (UTC+8)": "Asia/Singapore",
    "上海 (UTC+8)": "Asia/Shanghai",
    "曼谷 (UTC+7)": "Asia/Bangkok",
    "吉隆坡 (UTC+8)": "Asia/Kuala_Lumpur",
    "伊斯坦堡 (UTC+3)": "Europe/Istanbul",
    "杜拜 (UTC+4)": "Asia/Dubai",
    "卡拉奇 (UTC+5)": "Asia/Karachi",
    "加爾各答 (UTC+5:30)": "Asia/Kolkata",
    "開羅 (UTC+2)": "Africa/Cairo",
    "約翰內斯堡 (UTC+2)": "Africa/Johannesburg",
    "莫斯科 (UTC+3)": "Europe/Moscow",
    "巴黎 (UTC+1)": "Europe/Paris",
    "柏林 (UTC+1)": "Europe/Berlin",
    "倫敦 (UTC+0)": "Europe/London",
    "里斯本 (UTC+0)": "Europe/Lisbon",
    "聖保羅 (UTC-3)": "America/Sao_Paulo",
    "紐約 (UTC-5)": "America/New_York",
    "多倫多 (UTC-5)": "America/Toronto",
    "墨西哥城 (UTC-6)": "America/Mexico_City",
    "洛杉磯 (UTC-8)": "America/Los_Angeles",
    "檀香山 (UTC-10)": "Pacific/Honolulu",
}

HOURS = [f"{i:02d}" for i in range(24)]
MINUTES = [f"{i:02d}" for i in range(60)]

class CountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.last_notification_time = 0
        self.notification_count = 0
        self.sent_notifications = set()  # 記錄已發送的通知編號
        self.whatsapp_driver = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("倒數計時")
        self.setFixedSize(900, 650)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("倒數計時")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        tz_layout = QHBoxLayout()
        tz_layout.addWidget(QLabel("時區:"))
        self.tz_combo = QComboBox()
        self.tz_combo.addItems(TIMEZONES.keys())
        self.tz_combo.setStyleSheet("font-size: 16px; padding: 8px;")
        self.tz_combo.setFixedWidth(200)
        tz_layout.addWidget(self.tz_combo)
        tz_layout.addWidget(QLabel("日期:"))
        self.date_combo = QComboBox()
        today = QDate.currentDate()
        for i in range(30):
            d = today.addDays(i)
            self.date_combo.addItem(d.toString("yyyy-MM-dd"))
        self.date_combo.setStyleSheet("font-size: 16px; padding: 8px;")
        self.date_combo.setFixedWidth(150)
        tz_layout.addWidget(self.date_combo)
        tz_layout.addWidget(QLabel("時:"))
        self.hour_combo = QComboBox()
        self.hour_combo.addItems(HOURS)
        self.hour_combo.setStyleSheet("font-size: 16px; padding: 8px;")
        self.hour_combo.setFixedWidth(80)
        tz_layout.addWidget(self.hour_combo)
        tz_layout.addWidget(QLabel("分:"))
        self.minute_combo = QComboBox()
        self.minute_combo.addItems(MINUTES)
        self.minute_combo.setStyleSheet("font-size: 16px; padding: 8px;")
        self.minute_combo.setFixedWidth(80)
        tz_layout.addWidget(self.minute_combo)
        tz_layout.addStretch()
        main_layout.addLayout(tz_layout)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("輸入通知主題")
        self.message_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.message_input.setFixedWidth(400)
        main_layout.addWidget(self.message_input, alignment=Qt.AlignmentFlag.AlignCenter)

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("WhatsApp:"))
        phone_layout.addSpacing(10)
        
        self.phone_group = QButtonGroup()
        self.phone_radio1 = QRadioButton("+886922555330")
        self.phone_radio2 = QRadioButton("+886935742667")
        self.phone_radio1.setStyleSheet("color: white; font-size: 16px;")
        self.phone_radio2.setStyleSheet("color: white; font-size: 16px;")
        self.phone_radio1.setChecked(True)
        
        self.phone_group.addButton(self.phone_radio1)
        self.phone_group.addButton(self.phone_radio2)
        
        phone_layout.addWidget(self.phone_radio1)
        phone_layout.addWidget(self.phone_radio2)
        phone_layout.addStretch()
        main_layout.addLayout(phone_layout)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("開始倒數")
        self.start_btn.setStyleSheet("font-size: 18px; padding: 12px 40px; background: #007bff; color: white;")
        self.start_btn.clicked.connect(self.start_countdown)
        btn_layout.addWidget(self.start_btn)

        self.reset_btn = QPushButton("重新設定")
        self.reset_btn.setStyleSheet("font-size: 18px; padding: 12px 40px; background: #6c757d; color: white;")
        self.reset_btn.clicked.connect(self.reset_countdown)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.display = QLabel("00天 00:00:00")
        self.display.setStyleSheet("color: white; background: rgba(0,0,0,40%); padding: 25px; border-radius: 10px; font-weight: bold;")
        display_font = self.display.font()
        display_font.setPointSize(48)
        self.display.setFont(display_font)
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.display)

        self.tpe_time_display = QLabel("")
        self.tpe_time_display.setStyleSheet("color: #aaa;")
        tpe_font = self.tpe_time_display.font()
        tpe_font.setPointSize(14)
        self.tpe_time_display.setFont(tpe_font)
        self.tpe_time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.tpe_time_display)

        self.setLayout(main_layout)

    def get_selected_phone(self):
        if self.phone_radio1.isChecked():
            return "+886922555330"
        else:
            return "+886935742667"

    def calculate_notify_times(self):
        target_dt = datetime.fromtimestamp(self.target_time / 1000)

        # 時間到開始，每10分鐘通知一次，共15次
        notify_times = []
        for i in range(15):
            notify_time = target_dt + timedelta(minutes=i*10)
            notify_times.append(notify_time)

        times_str = f"⏰ 時間到開始提醒: {target_dt.strftime('%H:%M')}\n"
        times_str += f"⏰ 之後每10分鐘提醒一次 (共15次):\n"
        for i, t in enumerate(notify_times, 1):
            times_str += f"  {i:2d}. {t.strftime('%H:%M')}\n"
        times_str += f"  (持續到 {notify_times[-1].strftime('%H:%M')}，共2小時20分)"

        return times_str

    def send_whatsapp_initial(self, message):
        phone = self.get_selected_phone()
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        thread = threading.Thread(target=self.send_whatsapp_initial_thread, args=(phone, message))
        thread.daemon = True
        thread.start()

    def send_whatsapp_initial_thread(self, phone, message):
        import os
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            import time

            service = Service()
            user_data_dir = os.path.join(os.getcwd(), "whatsapp_data")

            # 確保目錄存在
            os.makedirs(user_data_dir, exist_ok=True)

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                print("正在打開 WhatsApp Web...")
                driver.get("https://web.whatsapp.com")
                print("等待 WhatsApp Web 載入中...")
                time.sleep(20)  # 增加等待時間

                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                print(f"正在打開聊天: {phone}")
                driver.get(url)
                time.sleep(15)  # 增加等待時間

                wait = WebDriverWait(driver, 60)
                print("等待聊天界面載入...")
                wait.until(EC.presence_of_element_located((By.ID, "side")))
                print("聊天界面已加載")
                time.sleep(3)

                # 多重回退策略嘗試發送
                print("嘗試發送訊息...")

                for attempt in range(5):
                    try:
                        print(f"  方法1: 尋找 data-tab='9'...")
                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="9"]')
                        input_box.send_keys(Keys.ENTER)
                        print("  ✓ 訊息已發送 (方法1)")
                        time.sleep(2)
                        return
                    except Exception as e:
                        time.sleep(2)

                for attempt in range(5):
                    try:
                        print(f"  方法2: 尋找 data-tab='1'...")
                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]')
                        input_box.send_keys(Keys.ENTER)
                        print("  ✓ 訊息已發送 (方法2)")
                        time.sleep(2)
                        return
                    except Exception as e:
                        time.sleep(2)

                for attempt in range(5):
                    try:
                        print(f"  方法3: 尋找 footer contenteditable...")
                        input_box = driver.find_element(By.CSS_SELECTOR, "footer div[contenteditable='true']")
                        input_box.send_keys(Keys.ENTER)
                        print("  ✓ 訊息已發送 (方法3)")
                        time.sleep(2)
                        return
                    except Exception as e:
                        time.sleep(2)

                try:
                    print("  方法4: 尋找發送按鈕 (data-testid)...")
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        try:
                            data_testid = btn.get_attribute("data-testid")
                            if data_testid and "send" in data_testid.lower():
                                btn.click()
                                print("  ✓ 訊息已發送 (方法4)")
                                time.sleep(2)
                                return
                        except:
                            continue
                except Exception as e:
                    pass

                try:
                    print("  方法5: 尋找發送按鈕 (data-icon)...")
                    send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']/parent::button")
                    send_button.click()
                    print("  ✓ 訊息已發送 (方法5)")
                    time.sleep(2)
                    return
                except Exception as e:
                    print(f"  ✗ 無法找到發送按鈕: {e}")

            finally:
                time.sleep(3)
                driver.quit()

        except Exception as e:
            import traceback
            print(f"初始 WhatsApp 發送錯誤: {e}")
            print(traceback.format_exc())

    def start_countdown(self):
        phone = self.get_selected_phone()

        tz_name = list(TIMEZONES.keys())[self.tz_combo.currentIndex()]
        tz_value = TIMEZONES[tz_name]

        from zoneinfo import ZoneInfo
        date_str = self.date_combo.currentText()
        year, month, day = map(int, date_str.split('-'))
        hour = self.hour_combo.currentIndex()
        minute = self.minute_combo.currentIndex()

        target_tz = ZoneInfo(tz_value)
        target_dt = datetime(year, month, day, hour, minute, 0, tzinfo=target_tz)
        self.target_time = int(target_dt.timestamp() * 1000)

        # 計算預計發送時間
        notify_times = self.calculate_notify_times()

        # 發送預計時間通知並打開WhatsApp
        message = self.message_input.text().strip() or "倒數計時"
        self.send_whatsapp_initial(f"【預計通知時間】{message}\n{notify_times}")

        self.start_btn.setText("倒數中...")
        self.start_btn.setEnabled(False)
        self.last_notification_time = 0
        self.notification_count = 0
        self.sent_notifications.clear()

        # 更新TPE時間顯示
        from zoneinfo import ZoneInfo
        tpe_tz = ZoneInfo("Asia/Taipei")
        target_dt_utc = datetime.fromtimestamp(self.target_time / 1000, tz=ZoneInfo("UTC"))
        target_dt_tpe = target_dt_utc.astimezone(tpe_tz)
        tpe_time_str = target_dt_tpe.strftime("%Y年%m月%d日 %H:%M:%S")
        self.tpe_time_display.setText(f"TPE時間: {tpe_time_str}")

        self.timer.start(100)

    def reset_countdown(self):
        self.timer.stop()
        self.display.setText("00天 00:00:00")
        self.tpe_time_display.setText("")
        self.start_btn.setText("開始倒數")
        self.start_btn.setEnabled(True)
        self.last_notification_time = 0
        self.notification_count = 0
        self.sent_notifications.clear()

    def send_whatsapp_thread(self, phone, message):
        import os
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            import time

            service = Service()
            user_data_dir = os.path.join(os.getcwd(), "whatsapp_data")

            # 確保目錄存在
            os.makedirs(user_data_dir, exist_ok=True)

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                print("打開 WhatsApp Web...")
                driver.get("https://web.whatsapp.com")
                print("等待 WhatsApp Web 載入...")
                time.sleep(15)

                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                print(f"打開聊天窗口: {phone}")
                driver.get(url)
                print("等待聊天界面...")
                time.sleep(12)

                wait = WebDriverWait(driver, 60)

                wait.until(EC.presence_of_element_located((By.ID, "side")))
                print("聊天界面已加載，開始發送訊息...")
                time.sleep(3)

                for attempt in range(5):
                    try:
                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="9"]')
                        input_box.send_keys(Keys.ENTER)
                        print("✓ 訊息已發送 (方法1)")
                        time.sleep(2)
                        return
                    except:
                        time.sleep(2)
                
                for attempt in range(5):
                    try:
                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]')
                        input_box.send_keys(Keys.ENTER)
                        print("✓ 訊息已發送 (方法2)")
                        time.sleep(2)
                        return
                    except:
                        time.sleep(2)

                for attempt in range(5):
                    try:
                        input_box = driver.find_element(By.CSS_SELECTOR, "footer div[contenteditable='true']")
                        input_box.send_keys(Keys.ENTER)
                        print("✓ 訊息已發送 (方法3)")
                        time.sleep(2)
                        return
                    except:
                        time.sleep(2)

                try:
                    print("尋找發送按鈕...")
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        try:
                            data_testid = btn.get_attribute("data-testid")
                            if data_testid and "send" in data_testid.lower():
                                btn.click()
                                print("✓ 訊息已發送 (方法4)")
                                time.sleep(2)
                                return
                        except:
                            continue
                except Exception as e:
                    pass

                try:
                    send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']/parent::button")
                    send_button.click()
                    print("✓ 訊息已發送 (方法5)")
                    time.sleep(2)
                    return
                except Exception as e:
                    print(f"✗ 無法找到發送按鈕: {e}")

            finally:
                time.sleep(3)
                driver.quit()

        except Exception as e:
            import traceback
            print(f"WhatsApp 發送錯誤: {e}")
            print(traceback.format_exc())

    def send_whatsapp(self, message):
        phone = self.get_selected_phone()
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        thread = threading.Thread(target=self.send_whatsapp_thread, args=(phone, message))
        thread.daemon = True
        thread.start()

    def update_countdown(self):
        now_ms = int(datetime.now().timestamp() * 1000)
        diff = self.target_time - now_ms
        current_time = int(datetime.now().timestamp() * 1000)

        # 時間到開始通知，每10分鐘通知一次，共15次
        if diff <= 0:
            elapsed = current_time - self.target_time

            # 計算目前應該在第幾次通知
            current_notification_num = int(elapsed / (10 * 60 * 1000)) + 1
            current_notification_num = min(current_notification_num, 15)  # 最多15次

            # 檢查這個通知編號是否已經發送過
            if current_notification_num not in self.sent_notifications and current_notification_num <= 15:
                self.sent_notifications.add(current_notification_num)
                message = self.message_input.text().strip() or "倒數計時"
                now_str = QDateTime.currentDateTime().toString("HH:mm:ss")

                if current_notification_num == 1:
                    self.send_whatsapp(f"【時間到】{message} (第 1/15 次) ({now_str})")
                else:
                    self.send_whatsapp(f"【提醒】{message} (第 {current_notification_num}/15 次) ({now_str})")

            # 15次通知後停止（共140分鐘 = 2小時20分）
            if current_notification_num >= 15:
                self.timer.stop()
                self.start_btn.setText("開始倒數")
                self.start_btn.setEnabled(True)
                return

        # 顯示倒數或正數
        if diff >= 0:
            # 倒數
            days = diff // (1000 * 60 * 60 * 24)
            hours = (diff % (1000 * 60 * 60 * 24)) // (1000 * 60 * 60)
            minutes = (diff % (1000 * 60 * 60)) // (1000 * 60)
            seconds = (diff % (1000 * 60)) // 1000
            self.display.setText(f"{int(days):02d}天 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        else:
            # 正數（已過時間）
            elapsed = -diff
            days = elapsed // (1000 * 60 * 60 * 24)
            hours = (elapsed % (1000 * 60 * 60 * 24)) // (1000 * 60 * 60)
            minutes = (elapsed % (1000 * 60 * 60)) // (1000 * 60)
            seconds = (elapsed % (1000 * 60)) // 1000
            self.display.setText(f"+{int(days):02d}天 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountdownWindow()
    window.show()
    sys.exit(app.exec())