# dogcat.star login automation

This is a project with a playwright's automation to [Dogcat.Star](https://www.dogcatstar.com/) website
Including Login Modules with test cases:
| No. | Feature File | Description                                           |
|-----|--------------|-------------------------------------------------------|
| 1   | 1.feature    | I can login successfully with email and password     |
| 2   | 2.feature    | I can login successfully with email and Verification Code |
| 3   | 12.feature   | I can login successfully with phone verification code |
| 4   | 10.feature   | I can login successfully with my line account         |
| 5   | 11.feature   | I can login successfully with my facebook account     |

## 🧰 Test Tools
| Tool/Service            | Description                                |
|-------------------------|--------------------------------------------|
| [Temp Email](https://mail.tm/en/)          | 用於測試的臨時信箱                       |
| [SMS](https://console.twilio.com/us1/monitor/logs/sms) | Twilio 平台上的 SMS 記錄查詢              |
| Test Case Management    | TestRail 測試案例管理平台                   |
| Automation Framework    | PlayWright 自動化測試框架                  |

### 📧 Email & SMS Automation Setup

1️⃣ Using Temp Mail API for Email Automation
🔹 Utilizing [mail.tm API](https://mail.tm) to handle all email-related workflows efficiently.

📌 **Temp Mail Preview:**
![temp mail](https://github.com/tsailiting/dogcat/blob/main/images/temp_mail.png)

---

2️⃣ Using Twilio for SMS Automation
🔹 Integrating [Twilio Programmable Messaging API](https://console.twilio.com/us1/monitor/logs/sms) to handle SMS operations.

📌 **Twilio SMS Preview:**
![temp sms](https://github.com/tsailiting/dogcat/blob/main/images/twilio.png)

## Set up
```
sh scripts/setup.sh
```
Enter poetry
```
poetry shell
```
For more commands for poetry, see https://python-poetry.org/docs/cli/

### Test Codegen

If all goes well, that should open two windows.

```
playwright codegen google.com
```
Run Pytest DEBUG mode
```
PWDEBUG=1 pytest -m “app-smoke”
```

### Install and setting XQuartz
1. Install XQuartz in local device 
```
brew install --cask xquartz
```
2. Open XQuartz, go to Preferences -> Security, and check “Allow connections from network clients”
3. Restart your computer (restarting XQuartz might not be enough)
4. Start XQuartz by local Terminal
```
xhost +localhost
```
## Execute
Execute the playwright with pytest print out
```
pytest -s -m “login”
```



## Result
![Test Cases](https://github.com/tsailiting/dogcat/blob/main/images/testcases.png)

### TestRail integration
Update test result to testrail
```
python testrail.py -run_id=<your_test_run_id>
```
### Update test result with JUnit XML format

- 📌 [JUnit Parser Documentation](https://junitparser.readthedocs.io/en/latest/)

![JUnit XML Example](https://github.com/tsailiting/dogcat/blob/main/images/junit.png)

### Automation Result on TestRail
![Test Result](https://github.com/tsailiting/dogcat/blob/main/images/test_results.png)
