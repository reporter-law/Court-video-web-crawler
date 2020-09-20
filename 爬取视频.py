"""程序说明"""
# -*-  coding: utf-8 -*-
# Author: cao wang
# Datetime : 2020
# software: PyCharm
# 收获:
import requests,os,re,time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from retrying import retry
from selenium.webdriver.chrome.options import Options
from 常用设置.进程与线程.线程方法化 import Thread_Pool as tp
from m3u8_download import main as m
class M3u8_Requests():
    """#ffmpeg"""
    def __init__(self,page=20):
        self.page = page
        today = datetime.today()
        today = today.strftime("%m-%d%H%M%S")
        self.path = os.path.abspath(os.path.dirname(__file__)) + "\\庭审直播\\{}".format(today)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    retry(stop_max_attempt_number=3)
    def url_get(self):
        base_url = "http://tingshen.court.gov.cn/video"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10, 0.1)
        self.browser.get(base_url)
        lis = []
        for i in range(self.page):
            button  = self.wait.until(EC.element_to_be_clickable( (By.XPATH, '//*[@id="result_div"]/div[2]/span')))
            button.click()
            time.sleep(2)
        self.browser.execute_script("window.stop()")

        for i in range(1,7):
            url = self.wait.until(EC.element_to_be_clickable((By.XPATH,f'//*[@id="case_list"]/li[{i}]/div[2]/div[1]/a[2]')))
            url.click()
            self.browser.switch_to.window(self.browser.window_handles[1])
            frame = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrapper"]/div[4]/div[2]/div[1]/iframe')))
            self.browser.execute_script("window.stop()")
            m3u8 = frame.get_attribute("src")
            print(m3u8)
            lis.append(m3u8)
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])
        for i in range(1,self.page * 15):
            try:
                url = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="result_div"]/li[{i}]/div[2]/div[1]/a[2]')))
                url.click()
            except:
                pass
            self.browser.switch_to.window(self.browser.window_handles[1])
            try:
                frame = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrapper"]/div[4]/div[2]/div[1]/iframe')))
                self.browser.execute_script("window.stop()")
                m3u8 = frame.get_attribute("src")
                print(m3u8)
                lis.append(m3u8)
            except:
                self.browser.refresh()
                try:
                    frame = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="wrapper"]/div[4]/div[2]/div[1]/iframe')))
                    m3u8 = frame.get_attribute("src")
                    lis.append(m3u8)
                except:
                    pass
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])

        with open(self.path+"\\url.txt","a+")as f:
            for i in lis:
                f.write(i+"\n")
        self.browser.quit()
    @retry(stop_max_attempt_number=3)
    def ffmpeg_m3u8(self,url):
        global m3u8
        url = url.strip("\n")
        r = requests.get(url)
        test_lis = []
        try:
            m3u8 = re.findall('"(.*?).m3u8', r.text)[0] + ".m3u8"
            print(m3u8+"\n")
            test_lis.append(m3u8)
        except:
            print(f"失败的url为{url}")
        print(f"一共{len(test_lis)}个m3u8")
        file = self.path + "\\" + m3u8.split("/")[-1]
        m(m3u8,file)
        #os.system(f"m3_dl {m3u8} -o {file}")
        print("下载成功>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    def main(self):
        self.url_get()
        with open(self.path+ r"\\url.txt", "r+")as f:
            urls = f.readlines()
            print(f"一共{len(urls)}个url")
        try:
            tp(10,self.ffmpeg_m3u8,urls).concurrent_Thread_package()
        except:
            pass
if __name__ =="__main__":
    M3u8_Requests().main()
