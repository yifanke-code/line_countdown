# LINE 倒數計時 使用手冊

## 目錄
1. [概述](#概述)
2. [系統需求](#系統需求)
3. [安裝步驟](#安裝步驟)
4. [快速開始](#快速開始)
5. [使用說明](#使用說明)
6. [命令列參數](#命令列參數)
7. [時區設定](#時區設定)
8. [日期時間格式](#日期時間格式)
9. [接收對象管理](#接收對象管理)
10. [常見問題](#常見問題)
11. [進階用法](#進階用法)

---

## 概述

**LINE 倒數計時**是一個命令列版本的倒數計時工具，可在指定時間通過 LINE 傳送提醒訊息給一個或多個接收者。

### 主要功能
- 🕐 倒數計時至指定時間
- 📱 通過 LINE 自動傳送通知
- 🌍 支援多種時區格式
- 👥 可傳送給多個接收對象
- ⏰ 10 次自動提醒通知（從目標時間前 10 分鐘開始）

### 通知時程表
- **第 1/10 次** - 目標時間前 10 分鐘（預告）
- **第 2/10 次** - 目標時間（時間到）
- **第 3-10 次** - 每 10 分鐘傳送一次提醒

---

## 系統需求

### 硬體需求
- 任何可執行 Python 的作業系統（Linux、macOS、Windows）
- 網際網路連接
- 至少 100MB 可用空間

### 軟體需求
- **Python 3.8+**（建議 3.9 或更新版本）
- **pip**（Python 套件管理工具）
- LINE 帳戶和 LINE Messaging API 存取令牌

---

## 安裝步驟

### 1. 安裝 Python 依賴套件

```bash
# 安裝 LINE Bot SDK
pip install line-bot-sdk
```

### 2. 設定 LINE Channel Access Token

需要設定環境變數 `LINE_CHANNEL_ACCESS_TOKEN`。

#### Linux / macOS：
```bash
# 臨時設定（僅當前終端機會話有效）
export LINE_CHANNEL_ACCESS_TOKEN="your_access_token_here"

# 永久設定（編輯 ~/.bashrc 或 ~/.zshrc）
echo 'export LINE_CHANNEL_ACCESS_TOKEN="your_access_token_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)：
```powershell
# 臨時設定
$env:LINE_CHANNEL_ACCESS_TOKEN = "your_access_token_here"

# 永久設定（編輯系統環境變數）
[System.Environment]::SetEnvironmentVariable("LINE_CHANNEL_ACCESS_TOKEN", "your_access_token_here", "User")
```

### 3. 設定接收對象

編輯 `countdown_linux.py` 檔案中的 `LINE_RECIPIENTS` 字典：

```python
LINE_RECIPIENTS = {
    "U62f156ab5afd221576ea85039ac4ed21": "Evan",
    "U40c729ba870837553332a7179e97f854": "Cheryl",
    "Ca1234567890abcdef1234567890abc": "Group Chat 1",
}
```

**如何取得 LINE User ID？**
- 個人用戶：可通過 LINE 官方帳號或 Bot 的 webhook 取得
- 群組：群組 ID 通常以 `C` 開頭

---

## 快速開始

### 最簡單的用法

```bash
python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -u=Evan
```

**參數說明：**
- `-tz=Asia/Taipei` - 設定時區為台北時間（UTC+8）
- `-dt=2605201722` - 目標時間為 2026年05月20日 17:22
- `-u=Evan` - 傳送給名叫 Evan 的接收者

---

## 使用說明

### 執行程式

```bash
python countdown_linux.py [選項]
```

### 程式輸出範例

```
============================================================
LINE 倒數計時 - 命令列版本
============================================================
時區: Asia/Taipei
目標時間: 2026年05月20日 17:22:00
通知主題: 重要會議
接收對象: Evan, Cheryl
============================================================
⏰ 倒數開始時間
05-20 Asia/Taipei: 17:22
05-20 Taipei time: 17:22
============================================================

開始倒數...

[14:32:15] 【預告】重要會議 (第 1/10 次) (14:32:15)
[17:22:00] 【時間到】重要會議 (第 2/10 次) (17:22:00)
[17:32:00] 【提醒】重要會議 (第 3/10 次) (17:32:00)
...
✓ 倒數完成！已發送全部10次通知
```

### 中止倒數

按下 `Ctrl+C` 可隨時中止程式：

```
倒數時間: 00天 05:14:32
^C
⚠ 倒數已中止
```

---

## 命令列參數

| 參數 | 簡寫 | 說明 | 必需 | 範例 |
|------|------|------|------|------|
| `--timezone` | `-tz` | 時區 | ✓ | `-tz=Asia/Taipei` |
| `--datetime` | `-dt` | 目標日期時間（10位數） | ✓ | `-dt=2605201722` |
| `--message` | `-m` | 通知主題（預設：倒數計時） | ✗ | `-m=Hello` |
| `--user` | `-u` | 接收對象名稱（可重複） | ✓ | `-u=Evan -u=Cheryl` |

### 參數詳細說明

#### `-tz` / `--timezone`（必需）
設定倒數的時區。支援以下格式：

- 時區縮寫：`CDT`, `EST`, `PST`, `JST`, `HKT`, `SGT` 等
- UTC 偏移：`UTC+8`, `UTC-5`, `UTC+0` 等
- IANA 時區：`Asia/Taipei`, `America/New_York`, `Europe/London` 等

#### `-dt` / `--datetime`（必需）
目標日期時間，使用 10 位數格式：`YYMMDDHHMI`

- `YY` - 年份（2 位，範圍 00-99，解釋為 2000-2099）
- `MM` - 月份（2 位，範圍 01-12）
- `DD` - 日期（2 位，範圍 01-31）
- `HH` - 小時（2 位，範圍 00-23）
- `MI` - 分鐘（2 位，範圍 00-59）

#### `-m` / `--message`（選用）
通知訊息的主題。若未指定，預設為「倒數計時」。
不支援空格；若需要空格，請用底線 `_` 代替，或用引號括住。

#### `-u` / `--user`（必需，可重複）
接收訊息的對象名稱。必須至少指定一個接收者。
可多次使用 `-u` 參數來指定多個接收者。

---

## 時區設定

### 支援的時區縮寫

| 縮寫 | IANA 時區 | GMT 偏移 |
|------|----------|---------|
| CDT | America/Chicago | UTC-5 |
| CST | America/Chicago | UTC-6 |
| EDT | America/New_York | UTC-4 |
| EST | America/New_York | UTC-5 |
| PDT | America/Los_Angeles | UTC-7 |
| PST | America/Los_Angeles | UTC-8 |
| GMT | UTC | UTC+0 |
| UTC | UTC | UTC+0 |
| JST | Asia/Tokyo | UTC+9 |
| IST | Asia/Kolkata | UTC+5:30 |
| SGT | Asia/Singapore | UTC+8 |
| HKT | Asia/Hong_Kong | UTC+8 |

### 使用 UTC 偏移

```bash
# 東部時間（UTC-5）
python countdown_linux.py -tz=UTC-5 -dt=2605201722 -u=Evan

# 中原標準時間（UTC+8）
python countdown_linux.py -tz=UTC+8 -dt=2605201722 -u=Evan

# UTC 時間
python countdown_linux.py -tz=UTC+0 -dt=2605201722 -u=Evan
```

### 使用 IANA 時區

完整 IANA 時區清單：https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

```bash
# 台北時間
python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -u=Evan

# 紐約時間
python countdown_linux.py -tz=America/New_York -dt=2605201722 -u=Evan

# 倫敦時間
python countdown_linux.py -tz=Europe/London -dt=2605201722 -u=Evan
```

---

## 日期時間格式

### 格式說明

日期時間使用 **10 位數字格式** `YYMMDDHHMI`：

```
2605201722
││││││││││
││││││││└─ 分鐘 (22)
│││││││└── 小時 (17)
││││││└─── 日期 (20)
│││││└──── 月份 (05)
││└─────── 年份 (26 = 2026)
```

### 範例

| 日期時間 | 碼字 | 說明 |
|----------|------|------|
| 2026年5月20日 17:22 | `2605201722` | 5月20日下午5點22分 |
| 2026年12月31日 23:59 | `2612312359` | 12月31日晚上11點59分 |
| 2025年1月1日 00:00 | `2501010000` | 1月1日午夜 |
| 2027年6月15日 14:30 | `2706151430` | 6月15日下午2點30分 |

### 時間轉換計算機

若要快速轉換日期時間，可參考以下方法：

```python
from datetime import datetime

# 將日期時間轉換為 10 位數碼
dt = datetime(2026, 5, 20, 17, 22)
code = dt.strftime("%y%m%d%H%M")
print(code)  # 輸出：2605201722

# 將 10 位數碼轉換為日期時間
code = "2605201722"
dt = datetime.strptime(code, "%y%m%d%H%M")
print(dt)  # 輸出：2026-05-20 17:22:00
```

---

## 接收對象管理

### 查看可用的接收對象

在 `countdown_linux.py` 中的 `LINE_RECIPIENTS` 字典中查看：

```python
LINE_RECIPIENTS = {
    "U62f156ab5afd221576ea85039ac4ed21": "Evan",
    "U40c729ba870837553332a7179e97f854": "Cheryl",
    "Ca1234567890abcdef1234567890abc": "Group Chat 1",
}
```

程式會自動顯示可用的使用者列表：

```bash
$ python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -u=Unknown
✗ 錯誤: 無法找到使用者 'Unknown'
  可用的使用者: Evan, Cheryl, Group Chat 1
```

### 新增接收對象

1. 取得接收者的 LINE User ID
2. 編輯 `countdown_linux.py` 中的 `LINE_RECIPIENTS` 字典
3. 添加新的 `"user_id": "display_name"` 對應

```python
LINE_RECIPIENTS = {
    "U62f156ab5afd221576ea85039ac4ed21": "Evan",
    "U40c729ba870837553332a7179e97f854": "Cheryl",
    "Ca1234567890abcdef1234567890abc": "Group Chat 1",
    "U1234567890abcdef1234567890abcde": "新使用者",  # 新增此行
}
```

### 傳送給多個接收者

```bash
python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -m=重要會議 -u=Evan -u=Cheryl -u=Group_Chat_1
```

---

## 常見問題

### Q1: 出現「無效的時區」錯誤

```
✗ 錯誤: 無效的時區 'XYZ'
  支援格式: CDT, EST, UTC-3, Asia/Taipei, 等...
```

**解決方案：**
- 檢查時區拼寫是否正確（大小寫不敏感）
- 使用支援的時區縮寫或 IANA 時區名稱
- 若使用 UTC 偏移，確保格式為 `UTC+X` 或 `UTC-X`

### Q2: 出現「無效的日期時間格式」錯誤

```
✗ 錯誤: 無效的日期時間格式 '26-05-20-17:22'
  正確格式: 10位數 (如: 2605201722 => 2026/05/20 17:22)
```

**解決方案：**
- 確保日期時間為 10 位純數字，格式為 `YYMMDDHHMI`
- 不要包含任何特殊字符或空格
- 檢查月份（01-12）、日期（01-31）、小時（00-23）、分鐘（00-59）是否有效

### Q3: LINE 訊息無法發送

```
✗ LINE 發送錯誤: [Errno ...] ...
```

**檢查清單：**
1. 確認 `LINE_CHANNEL_ACCESS_TOKEN` 環境變數已正確設定
   ```bash
   echo $LINE_CHANNEL_ACCESS_TOKEN  # Linux/macOS
   echo %LINE_CHANNEL_ACCESS_TOKEN%  # Windows CMD
   ```

2. 確認 Access Token 有效且未過期
3. 確認接收者的 User ID 正確
4. 確認網際網路連接正常
5. 檢查 LINE 官方帳號的設定是否允許 Bot 傳送訊息

### Q4: 程式在啟動後立即結束

確認是否有任何參數錯誤：
- 檢查所有必需參數 (`-tz`, `-dt`, `-u`) 是否已指定
- 確認使用者名稱拼寫正確

### Q5: 倒數時間不準確

- 確認系統時間正確
- 考慮網路延遲可能導致的輕微差異（通常 ±1-2 秒）

### Q6: 我需要更改 LINE 接收對象

編輯 `countdown_linux.py` 中的 `LINE_RECIPIENTS` 字典：

```python
LINE_RECIPIENTS = {
    "新使用者ID": "新顯示名稱",
    # ...其他使用者
}
```

保存後重新執行程式即可。

---

## 進階用法

### 執行多個獨立倒數

在多個終端機視窗中同時執行不同的倒數計時：

```bash
# 終端機 1
python countdown_linux.py -tz=Asia/Taipei -dt=2605201722 -m=會議1 -u=Evan

# 終端機 2
python countdown_linux.py -tz=America/New_York -dt=2605201722 -m=會議2 -u=Cheryl
```

### 使用 Shell 腳本自動執行

創建 `schedule_countdown.sh`：

```bash
#!/bin/bash

# 會議 1 - 台北時間
python countdown_linux.py -tz=Asia/Taipei -dt=2605181400 -m=會議1 -u=Evan &

# 會議 2 - 紐約時間
python countdown_linux.py -tz=America/New_York -dt=2605181900 -m=會議2 -u=Cheryl &

wait
```

執行：
```bash
chmod +x schedule_countdown.sh
./schedule_countdown.sh
```

### 與 Cron 整合（自動定時執行）

編輯 crontab：
```bash
crontab -e
```

添加條目（例如：每天早上 8 點執行）：
```cron
0 8 * * * cd /path/to/project && python countdown_linux.py -tz=Asia/Taipei -dt=$(date +\%y\%m\%d)0900 -m=晨會 -u=Evan
```

### 自訂訊息格式

編輯 `countdown_linux.py` 的訊息格式部分（約 260 行）：

```python
# 自訂預告訊息
msg = f"【準備開始】{self.message} (倒數 1/10)"

# 自訂目標時間訊息
msg = f"【現在開始】{self.message}"

# 自訂提醒訊息
msg = f"【提醒】{self.message}（進行中）"
```

---

## 技術詳情

### 通知時程邏輯

程式在目標時間前 10 分鐘開始監控，並按以下時程傳送通知：

```
目標時間前 10 分鐘    ← 第 1/10 次（預告）
目標時間              ← 第 2/10 次（時間到）
目標時間 + 10 分鐘    ← 第 3/10 次
目標時間 + 20 分鐘    ← 第 4/10 次
...
目標時間 + 80 分鐘    ← 第 10/10 次
```

### 更新環境變數的優先級

環境變數查找順序：
1. 終端機會話的環境變數
2. 使用者級環境變數（`~/.bashrc` 等）
3. 系統級環境變數
4. `.env` 檔案（如果存在）

---

## 支援與反饋

若遇到任何問題或有功能建議，請：

1. 檢查本手冊的「常見問題」部分
2. 查看程式的錯誤訊息
3. 確認所有參數格式正確

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-06-15 | 初始發佈，支援 10 次通知 |

---

**最後更新日期：2026年6月15日**
