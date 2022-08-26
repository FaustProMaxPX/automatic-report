import datetime
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import json
import sys
import time
import logging
from logging import handlers
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

report_index_url = 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp'
report_url = 'https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp'
login_url = 'https://uis.nwpu.edu.cn/cas/login'
# 配置文件位置
conf_file = '/home/ubuntu/dev/python/info.json'
log_file = '/home/ubuntu/dev/python/report/tianbao.log'

rbxx_dict = {
    "学校": '1',
    "西安市内": '2',
    "国内": '3'
}

logger = None
mail_msg = "填报成功"

def get_logger(filename:str):
    """
    获取日志
    Args:
        filename (str): 日志文件保存位置
    """
    global logger
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    file_handler = handlers.RotatingFileHandler(filename=filename, maxBytes=1*1024*1024*1024, backupCount=1, encoding='utf-8')
    file_handler.setFormatter(fmt=fmt)
    # if enable_email:
    #     sh = logging.handlers.SMTPHandler(("smtp.163.com", 25), info['email']['username'],
    #                               ['1546327522@qq.com'],
    #                               datetime.date.today + "每日填报",
    #                               credentials=(info['email']['username'], info['email']['password']),
    #                               )
    #     sh.setFormatter(fmt=fmt)
    #     logger.addHandler(sh)
    logger.addHandler(file_handler)
    
    
def init_driver():
    """
    初始化谷歌驱动器
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def load_file(filename):
    with open(filename, 'r') as f:
        info = json.load(f)
    return info
    
def login(driver, info):
    """
    登录翱翔门户
    """
    driver.get(login_url)
    username = driver.find_element(by='id', value='username')
    username.clear()
    username.send_keys(info["username"])
    password = driver.find_element(by='id', value='password')
    password.clear()
    password.send_keys(info["password"])
    driver.find_element(by='name', value='submit').click()
    
    
    
def report(driver:webdriver, info, is_conf):
    """
    填报函数
    Args:
        driver (webdriver): 网页驱动器
        info (dict): 用户信息
        is_conf (bool): 是否使用配置文件中的地址填报, 若为False,则会直接使用之前填报记录的信息
    """
    # 我也不知道为什么不能直接去填报界面，但不先走首页，后面就会报错
    driver.get(report_index_url)
    driver.get(report_url)
    rbxx = info['address']['in']
    label_num = rbxx_dict[rbxx]
    driver.find_element(by=By.XPATH, value='//*[@class="layui-layer-btn0"]').click()
    if is_conf:
        v1 = '//*[@id="notlocation"]/' + 'label[' + label_num + ']'
        driver.find_element(by=By.XPATH, value=v1).click()
        
        time.sleep(1)
        
        if rbxx != "学校":
            if rbxx != "市内":
                s_province = driver.find_element(by=By.XPATH, value='//*[@id="province"]')
                province = Select(s_province)
                province.select_by_visible_text(info['address']['province'])
            if rbxx != "市内":
                s_city = driver.find_element(by=By.XPATH, value='//*[@id="city"]')
                city = Select(s_city)
                city.select_by_visible_text(info['address']['city'])
            s_district = driver.find_element(by=By.XPATH, value='//*[@id="district"]')
            district = Select(s_district)
            district.select_by_visible_text(info['address']['district'])
    
    driver.execute_script('''
    javascript:go_sub();                      
    ''')
    time.sleep(1)
    driver.execute_script('''
    document.getElementById('brcn').checked=true;
    ''')
    driver.execute_script('''
    javascript:save();
    ''')  
    
def send_email():
    """
    填报完毕后发送邮件
    """
    smtp_obj = smtplib.SMTP()
    smtp_obj.connect("smtp.163.com", 25)
    smtp_obj.login(info['email']['sender']['username'], info['email']['sender']['password'])
        
    msg = MIMEText(mail_msg, 'plain', 'utf-8')
    msg['From'] = Header("自动填报", 'utf-8')
    msg['To'] = Header('watermelon', 'utf-8')    
    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    subject = today + " 每日填报"
    msg['Subject'] = Header(subject, 'utf-8')
    sender = info['email']['sender']['username']
    receivers = info['email']['receivers']
    smtp_obj.send_message(msg, sender, receivers)

if __name__ == '__main__':
    info = load_file(conf_file)
    driver = init_driver()
    
        
    get_logger(log_file)
    logger.info("开始为%s疫情填报", info['username'])
    try:
        login(driver, info)
        report(driver, info, info['address']['enable'])
    except Exception as e:
        logging.info("find exception: %s", e)
        
        logger.error("打卡失败，请手动前往打卡")
        logger.error("find exception: %s", e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        mail_msg = "打卡失败，请手动前往打卡\n检测到错误：{}\n".format(e)
        logging.info("错误类型：{}\n堆栈信息：{}".format(exc_type, traceback.format_exc()))
        mail_msg += "错误类型：{}\n堆栈信息：{}".format(exc_type, traceback.format_exc())
    finally:
        if info['email']['enable']:
            try:
                send_email()
            except smtplib.SMTPException:
                logger.error("邮件发送失败")
    logger.info("填报结束")
    