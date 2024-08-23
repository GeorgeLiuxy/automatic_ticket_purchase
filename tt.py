import base64
import time
from io import BytesIO
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor

# 定义登录函数
def login(account):
    # 初始化 WebDriver
    chromedriver_path = "/Volumes/software/chromedriver-mac-arm64/chromedriver"
    driver = webdriver.Chrome(chromedriver_path)

    try:
        driver.get("https://sports.sjtu.edu.cn/pc/#/")

        # 点击“校内人员登录”按钮
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'el-button--primary')]"))
        )
        login_button.click()

        # 在登录页面中输入用户名和密码
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input-login-user"))
        )
        driver.find_element(By.ID, "input-login-user").send_keys(account["username"])
        driver.find_element(By.ID, "input-login-pass").send_keys(account["password"])

        # 处理验证码
        captcha_img_element = driver.find_element(By.ID, "captcha-img")

        # 截取验证码图片
        captcha_img_base64 = captcha_img_element.screenshot_as_base64

        # 将 Base64 编码的图片转换为 PIL Image 对象
        captcha_image = Image.open(BytesIO(base64.b64decode(captcha_img_base64)))

        # 使用 OCR 识别验证码
        captcha_text = pytesseract.image_to_string(captcha_image).strip()

        # 在验证码输入框中输入识别出的验证码
        driver.find_element(By.ID, "input-login-captcha").send_keys(captcha_text)

        # 点击登录按钮
        login_submit_button = driver.find_element(By.ID, "submit-password-button")
        login_submit_button.click()

        # 等待页面加载
        time.sleep(5)

        # 检查登录结果
        if "成功" in driver.page_source:
            print(f"账号 {account['username']} 登录成功！")
        else:
            print(f"账号 {account['username']} 登录失败，请检查账号、密码或验证码。")

    finally:
        # 关闭浏览器
        print("~~~~~~~~~~~~")

# 账号和密码列表
accounts = [
    {"username": "cherilyn.li", "password": "TuTu121866@"},
    # {"username": "cherilyn.li", "password": "TuTu121866@"},
    # 继续添加其他账号
]

# 使用 ThreadPoolExecutor 进行多账号同时登录
with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
    executor.map(login, accounts)
