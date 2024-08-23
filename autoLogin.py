import base64
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from io import BytesIO

import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 创建一个锁对象
lock = threading.Lock()


# 定义登录函数
def login_and_prepare(account):

    # 初始化 WebDriver
    chromedriver_path = "/Volumes/software/chromedriver-mac-arm64/chromedriver"
    option = webdriver.ChromeOptions()  # 默认Chrome浏览器
    # 关闭开发者模式, window.navigator.webdriver 控件检测到你是selenium进入，若关闭会导致出现滑块并无法进入。
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument('--disable-blink-features=AutomationControlled')
    # option.add_argument("--headless")  # 开启无头模式
    # option.add_argument("--disable-gpu")  # 适用于Windows环境
    # option.add_argument("--no-sandbox")  # 适用于Linux环境
    # option.add_argument('headless')               # Chrome以后台模式进行，注释以进行调试
    # option.add_argument('window-size=1920x1080')  # 指定分辨率
    # option.add_argument('no-sandbox')             # 取消沙盒模式
    # option.add_argument('--disable-gpu')          # 禁用GPU加速
    # option.add_argument('disable-dev-shm-usage')  # 大量渲染时候写入/tmp而非/dev/shm
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=option)
    driver.get("https://sports.sjtu.edu.cn/pc/#/")
    # 点击“校内人员登录”按钮
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'el-button--primary')]"))
    )
    login_button.click()
    login_successful = False
    while not login_successful:
        login_successful = do_login(account, driver, login_successful)

    # 选择球场类型
    choose_type(driver, "网球")
    # 选择并点击指定场地
    select_venue(driver, "子衿街南侧网球场")
    # 场地预定窗口已打开，准备可是抢票
    print("场地预定窗口已打开，准备开始抢票~~")
    # 等待到达目标时间
    # refresh_until_target_time("12:00:00")
    # 开始预定
    time.sleep(5)  # 等待一段时间以避免频繁请求
    run_booking_process(driver)

    # 关闭浏览器
    driver.quit()


def attempt_booking(driver):
    try:
        # 尝试找到并点击可预定的场地
        available_slots = driver.find_elements(By.XPATH, "//div[contains(@class, 'seat') and not(contains(@class, 'bought-seat'))]")
        if available_slots:
            for slot in available_slots:
                slot.click()
                print("已选定场地，准备下单...")
                break

            # 点击立即下单按钮
            order_button = driver.find_element(By.XPATH, "//button[contains(@class, 'el-button--primary') and contains(., '立即下单')]")
            order_button.click()
            print("下单成功！")
        else:
            print("没有找到可预定的场地，继续尝试...")
            return False
    except NoSuchElementException:
        print("操作失败，继续尝试...")
        return False

    return True


def run_booking_process(driver):
    # 选择日期
    select_next_wednesday_date()

    # 不断尝试预定
    while not attempt_booking():
        driver.refresh()  # 刷新页面继续尝试


def schedule_booking(accounts):

    # 使用 ThreadPoolExecutor 进行多账号同时登录
    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        executor.map(login_and_prepare, accounts)


def run_booking_process(driver):
    # 选择日期
    select_next_wednesday_date()

    # 不断尝试预定
    while not attempt_booking():
        driver.refresh()  # 刷新页面继续尝试


def get_next_wednesday_date():
    today = datetime.today()
    days_until_wednesday = (2 - today.weekday() + 7) % 7  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    if days_until_wednesday == 0:  # 如果今天是周三，抢下周三的
        days_until_wednesday = 7
    next_wednesday = today + timedelta(days=days_until_wednesday)
    return next_wednesday.strftime("%Y-%m-%d")


def refresh_until_target_time(target_time):
    while True:
        current_time = datetime.now().strftime('%H:%M:%S')
        if current_time >= target_time:
            break
        time.sleep(0.5)  # 每半秒刷新一次，检查时间


def select_next_wednesday_date(driver):
    next_wednesday_date = get_next_wednesday_date()
    target_date_tab = driver.find_element(By.XPATH, f"//div[contains(@id, 'tab-{next_wednesday_date}')]")
    target_date_tab.click()
    print(f"已选择日期: {next_wednesday_date}")


def do_login(account, driver, login_successful):
    # 输入用户名和密码
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-login-user"))
    )
    username_field = driver.find_element(By.ID, "input-login-user")
    username_field.clear()  # 清空文本框内容
    username_field.send_keys(account["username"])  # 填充用户名
    # 清空并填充密码
    password_field = driver.find_element(By.ID, "input-login-pass")
    password_field.clear()  # 清空文本框内容
    password_field.send_keys(account["password"])  # 填充密码
    # 使用线程锁，确保只有一个线程在操作验证码
    # 处理验证码
    captcha_img_element = driver.find_element(By.ID, "captcha-img")
    # 截取验证码图片
    captcha_img_base64 = captcha_img_element.screenshot_as_base64
    # 将 Base64 编码的图片转换为 PIL Image 对象
    captcha_image = Image.open(BytesIO(base64.b64decode(captcha_img_base64)))
    # 验证码图片处理
    captcha_text = pytesseract.image_to_string(captcha_image).strip()
    # 清空并填充密码
    captcha_field = driver.find_element(By.ID, "input-login-captcha")
    captcha_field.clear()  # 清空文本框内容
    captcha_field.send_keys(captcha_text)
    # 点击登录按钮
    login_submit_button = driver.find_element(By.ID, "submit-password-button")
    login_submit_button.click()
    time.sleep(3)
    # 检查登录是否成功
    if "个人信息" in driver.page_source:
        print("登录成功！")
        login_successful = True
    else:
        print("登录失败，可能是验证码错误。刷新页面重试...")
        time.sleep(2)  # 等待一段时间以避免频繁请求
    return login_successful


# 根据不同的区域或场地编号选择场地
def select_venue(driver, venue_name):
    # 等待场地列表加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cardUl"))
    )

    # 获取所有场地的列表项
    venues = driver.find_elements(By.CSS_SELECTOR, "ul.cardUl > li")

    # 遍历场地列表，找到匹配的场地并点击
    for venue in venues:
        venue_title = venue.find_element(By.CSS_SELECTOR, "h3").text
        if venue_title == venue_name:
            venue.click()
            print(f"已选择并点击场地: {venue_name}")
            return
    print(f"未找到指定的场地: {venue_name}")


def choose_type(driver, type_name):
    if type_name == "网球":
        # 登录成功后访问指定的场地页面
        driver.get("https://sports.sjtu.edu.cn/pc/#/Venue/1")
        # 等待页面加载并点击筛选网球场地的标签
        tennis_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(@class, 'el-radio-button') and contains(., '网球')]"))
        )
        tennis_label.click()

        print("已筛选出网球场地")


# 账号和密码列表
accounts = [
    {"username": "cherilyn.li", "password": "TuTu121866@"},
    # {"username": "cherilyn.li", "password": "TuTu121866@"},
    # 添加更多账号
]

# 设置每日12点定时任务
# schedule.ereryday.at("11:58").do(schedule_booking(accounts))  # 提前2分钟启动浏览器和登录操作

# while True:
#     schedule.run_pending()
#     time.sleep(1)

if __name__ == '__main__':
    schedule_booking(accounts)


