import base64
import datetime
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from io import BytesIO

import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_driver(low_flow):
    chromedriver_path = "/Volumes/software/chromedriver-mac-arm64/chromedriver"
    option = webdriver.ChromeOptions()
    if low_flow:
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_argument('--headless')  # 如果不需要显示界面，可以使用无头模式
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-extensions')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=option, desired_capabilities=capabilities)
        driver.request_interceptor = block_request
    else:
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=option)
    return driver


def block_request(request):
    blocked_resources = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.css', '*.js']
    for resource in blocked_resources:
        if resource in request['url']:
            return True
    return False


def solve_captcha(driver):
    # 这是一个示例函数，假设你有一个OCR算法来识别验证码
    captcha_text = solve_captcha(driver)  # 调用你的OCR识别函数
    return captcha_text.replace(" ", "")  # 去除识别结果中的空格


def login(account, driver):
    try:
        driver.get("https://sports.sjtu.edu.cn/pc/#/")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='button' and contains(@class, 'el-button--primary')]")
            )  # 登录按钮
        )
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input-login-user"))
        )
        username_field = driver.find_element(By.ID, "input-login-user")
        username_field.clear()
        username_field.send_keys(account["username"])

        password_field = driver.find_element(By.ID, "input-login-pass")
        password_field.clear()
        password_field.send_keys(account["password"])

        # 尝试自动识别验证码
        for attempt in range(10):  # 最多重试10次
            captcha_text = solve_captcha(driver)
            captcha_field = driver.find_element(By.ID, "input-login-captcha")
            captcha_field.clear()
            captcha_field.send_keys(captcha_text)

            login_submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submit-password-button"))
            )
            login_submit_button.click()

            time.sleep(3)  # 等待页面加载

            if "个人信息" in driver.page_source:
                logging.info(f"{account['username']} 登录成功")
                return True
            else:
                logging.warning(f"{account['username']} 登录失败，可能是验证码错误")

        logging.error(f"{account['username']} 登录失败，超过最大重试次数")
        return False

    except Exception as e:
        logging.error(f"{account['username']} 登录过程中出错: {e}")
        return False


def manual_captcha_input(driver):
    captcha_field = driver.find_element(By.ID, "input-login-captcha")
    captcha_text = input("请输入验证码: ")
    captcha_field.clear()
    captcha_field.send_keys(captcha_text)
    login_submit_button = driver.find_element(By.ID, "submit-password-button")
    login_submit_button.click()
    time.sleep(3)
    if "个人信息" in driver.page_source:
        return True
    return False


def solve_captcha(driver):
    captcha_img_element = driver.find_element(By.ID, "captcha-img")
    captcha_img_base64 = captcha_img_element.screenshot_as_base64
    captcha_image = Image.open(BytesIO(base64.b64decode(captcha_img_base64)))
    captcha_text = pytesseract.image_to_string(captcha_image).strip()
    logging.info(f"识别的验证码为: {captcha_text}")
    return captcha_text


def manual_captcha_input(driver):
    # 提示用户手动输入验证码
    captcha_text = input("自动识别失败，请手动输入验证码：")
    captcha_field = driver.find_element(By.ID, "input-login-captcha")
    captcha_field.clear()
    captcha_field.send_keys(captcha_text)

    # 再次尝试登录
    login_submit_button = driver.find_element(By.ID, "submit-password-button")
    login_submit_button.click()

    time.sleep(3)
    if "个人信息" in driver.page_source:
        logging.info("登录成功")
        return True
    else:
        logging.warning("手动验证码登录失败")
        return False


def select_court_type(driver, court_type):
    try:
        driver.get("https://sports.sjtu.edu.cn/pc/#/Venue/1")
        # 动态生成 XPath
        xpath_expression = f"//label[contains(@class, 'el-radio-button') and contains(., '{court_type}')]"
        tennis_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_expression))
        )
        tennis_label.click()
        logging.info("已筛选出" + court_type + "场地")
    except Exception as e:
        logging.error(f"选择场地类型失败: {e}")


def select_venue(driver, venue_name):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.cardUl > li"))
        )
        venues = driver.find_elements(By.CSS_SELECTOR, "ul.cardUl > li")
        for venue in venues:
            venue_title = venue.find_element(By.CSS_SELECTOR, "h3").text
            if venue_title == venue_name:
                venue.click()
                logging.info(f"已选择并点击场地: {venue_name}")
                return
        logging.warning(f"未找到指定的场地: {venue_name}")
    except NoSuchElementException:
        logging.error(f"选择场地时出现错误，未找到场地: {venue_name}")


def attempt_booking(driver, target_time):
    # 假设之前已经登录并选择了日期，这里直接查找并点击指定时间段的可选场地
    if find_and_click_first_available_seat_for_time(driver, target_time):
        # 继续执行后续操作，如点击“立即下单”按钮
        return click_order_button(driver)
    else:
        logging.info(f"在 {target_time} 未找到可预订的场地，或者选择失败。")
        return False


def click_order_button(driver):
    try:
        print("checkpoint 0 ~~~")
        # 等待“立即下单”按钮出现
        order_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'el-button--primary') and contains(., '立即下单')]"))
        )
        print("checkpoint 1 ~~~")
        # 点击“立即下单”按钮
        order_button.click()
        print("checkpoint 2 ~~~")
        # 等待对话框出现
        return accept_terms_and_submit_order(driver)
    except TimeoutException:
        logging.info("未能在指定时间内找到“立即下单”按钮。")
        return False
    except NoSuchElementException:
        logging.info("未找到“立即下单”按钮。")
        return False


def accept_terms_and_submit_order(driver):
    try:
        print("checkpoint 3 ~~~")
        # 显式等待元素出现，最多等待10秒
        checkbox_container = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-checkbox__input"))
        )
        print("checkpoint 4 ~~~")
        try:
            checkbox_container.click()
            logging.info("已选中复选框，同意协议。")
        except TimeoutException:
            logging.error("超时异常。")
            return False
        except NoSuchElementException:
            logging.error("未能找到复选框按钮。")
            return False

        # 在对话框中查找并点击“提交订单”按钮
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//div[@role='dialog']//button[contains(@class, 'el-button--primary') and contains(., '提交订单')]"))
        )
        submit_button.click()
        logging.info("已点击“提交订单”按钮。")

        return True

    except TimeoutException:
        logging.error("未能在指定时间内找到复选框或“提交订单”按钮。")
        return False
    except NoSuchElementException:
        logging.error("未找到复选框或“提交订单”按钮。")
        return False


def run_booking_process(driver, target_time, weekday):
    if select_next_wednesday_date(driver, weekday):
        logging.info(f"已选择日期: {get_next_wednesday_date(weekday)}")
    else:
        logging.error("选择日期失败")
        return False
    return attempt_booking(driver, target_time)


def get_next_wednesday_date(weekday):
    """
    根据当前日期，获取下周指定的星期几的日期
    :param weekday: 目标星期几，1=周一, 2=周二, ..., 7=周日
    :return: 下周目标日期的字符串，格式为 'YYYY-MM-DD'
    """
    today = datetime.today()
    days_ahead = int(weekday) - 1 - today.weekday() + 7
    if days_ahead <= 0:
        days_ahead += 7
    next_weekday = today + timedelta(days=days_ahead)
    return next_weekday.strftime("%Y-%m-%d")


def select_next_wednesday_date(driver, weekday):
    next_wednesday_date = get_next_wednesday_date(weekday)
    # 目标日期的ID
    target_date_id = "tab-" + str(next_wednesday_date)
    result = False
    try:
        # 等待“立即下单”按钮出现
        target_date_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@id, '{target_date_id}')]"))
        )
        target_date_tab.click()
        logging.info(f"已选择日期: {next_wednesday_date}")
        result = True
    except NoSuchElementException:
        logging.warning(f"未找到日期: {next_wednesday_date}，重新检查页面...")
        result = False
    finally:
        return result


def main(account, court_type, venue_name, target_time, weekday, booking_time, low_flow_mode):
    driver = setup_driver(low_flow_mode)
    login_successful = login(account, driver)
    if login_successful:
        select_court_type(driver, court_type)
        time.sleep(3)  # 等待页面加载
        select_venue(driver, venue_name)
        time.sleep(5)  # 等待页面加载
        logging.info("场地预定窗口已打开，正在进行时间校验")
        # 目标时间转为 datetime 对象
        target_time_obj = datetime.strptime(booking_time, "%H:%M").time()

        while True:
            current_time = datetime.now().time()
            logging.info(f"当前时间: {current_time}, 目标时间: {target_time_obj}")

            # 比较当前时间与目标时间
            if current_time >= target_time_obj:
                logging.info("时间已到达，准备开始抢票")
                break
            time.sleep(1)  # 稍等片刻再刷新，避免频繁刷新
            driver.refresh()  # 刷新页面

        # 一旦时间符合要求，立即执行预定流程
        if run_booking_process(driver, target_time, weekday):
            logging.info("抢票成功，请及时支付订单")
        else:
            logging.info("抢票失败，请稍后再试")

        time.sleep(2)  # 稍等片刻再刷新，避免频繁刷新
    driver.quit()  # 记得在任务结束后关闭浏览器


def schedule_booking(accounts, court_type, venue_name, target_time, weekday, booking_time, low_flow_mode):
    with ThreadPoolExecutor(max_workers=min(3, len(accounts))) as executor:
        for account in accounts:
            executor.submit(main, account, court_type, venue_name, target_time, weekday, booking_time, low_flow_mode)


def find_and_click_first_available_seat_for_time(driver, target_time):
    try:
        # 等待页面加载时间段和座位元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "leftUl"))
        )
        # 查找所有时间段
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='leftUl fl']/li"))
        )
        time_slots = driver.find_elements(By.XPATH, "//ul[@class='leftUl fl']/li")

        # 找到目标时间段的索引
        target_index = -1
        for index, time_slot in enumerate(time_slots):
            if time_slot.text.strip() == target_time:
                target_index = index
                break

        if target_index == -1:
            logging.info(f"未找到指定时间段: {target_time}")
            return False

        logging.info(f"已找到时间段 {target_time}，索引为 {target_index}")

        # 根据时间段索引，查找对应的可用座位
        seat_xpath = f"//div[@class='tables fl']//div[contains(@class, 'clearfix')][{target_index + 1}]//div[contains(@class, 'seat') and contains(@class, 'unselected-seat')]"
        available_seat = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, seat_xpath))
        )
        if available_seat:
            available_seat.click()
            logging.info(f"已选择 {target_time} 的一个可预订场地。")
            return True
        else:
            logging.info(f"在 {target_time} 未找到可预订的场地。")
            return False

    except TimeoutException:
        logging.error("加载可选座位超时，页面可能没有加载完全。")
        return False
    except NoSuchElementException:
        logging.error(f"未找到 {target_time} 的任何可选座位。")
        return False


if __name__ == '__main__':
    accounts = [
        {"username": "cherilyn.li", "password": "TuTu121866@"},
        # {"username": "cherilyn.li", "password": "TuTu121866@"},
        # 添加更多账号
    ]
    # 场地类型 "网球"
    # 场地名称 "xxx球场"
    # 预定时间区间 target_time "16:00"
    # param weekday: 目标星期几，1=周一, 2=周二, ..., 7=周日
    # booking_time 12:00
    booking_time = '12:00'
    schedule_booking(accounts, "网球", "东区网球场", "16:00", "1", booking_time, True)
