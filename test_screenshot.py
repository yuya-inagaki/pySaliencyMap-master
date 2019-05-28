# coding: utf-8

#--------------------------------------------------------------
#
#   スクリーンショット全体取得テスト用プログラム
#   作成日：2019.04.07
#
#--------------------------------------------------------------

import cv2
import matplotlib.pyplot as plt
import pySaliencyMap
import numpy as np
#get screenshot
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options #chrome使用のため
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary #firefox使用のため

from PIL import Image

#get html
import urllib2
#read html
from bs4 import BeautifulSoup
import re
#use csv
import csv
import pandas as pd


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst



# main
if __name__ == '__main__':

    browser_v = raw_input("使用するブラウザを入力してください Chrome:c Firefox:f\n")
    if browser_v == 'c':
        url = raw_input("URLを入力してください\n")
        print("ページの読み込み中...")


        # Open Web Browser & Resize
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        page_width = 1280
        page_height = driver.execute_script('return document.body.scrollHeight')
        print(page_width, page_height)
        if page_height > 3000:
            page_height = 3000
        driver.set_window_size(page_width, page_height)

        driver.save_screenshot('screenshot-chrome.png')



        # Close Web Browser
        driver.quit()

    else:
        url = raw_input("URLを入力してください\n")
        print("ページの読み込み中...")


        # Open Web Browser & Resize
        binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox')
        binary.add_command_line_options('-headless')
        driver = webdriver.Firefox(firefox_binary=binary)

        driver.get(url)
        window_width = 1280
        window_height = 800



        driver.set_window_size(window_width, window_height)

        page_height = driver.execute_script('return document.body.scrollHeight')
        scrollHeight = driver.execute_script('return window.innerHeight')

        print(scrollHeight)


        driver.save_screenshot('working/screenshot-firefox1.png')

        if page_height > scrollHeight*2 :
            driver.execute_script("window.scrollTo(0, "+str(scrollHeight)+");")
            driver.save_screenshot('working/screenshot-firefox2.png')

            im1 = Image.open('working/screenshot-firefox1.png')
            im2 = Image.open('working/screenshot-firefox2.png')
            get_concat_v(im1, im2).save('output/final_screenshot.png')

        elif page_height > scrollHeight :
            driver.execute_script("window.scrollTo(0, "+str(page_height - scrollHeight)+");")
            driver.save_screenshot('working/screenshot-firefox2.png')
            
            im1 = Image.open('working/screenshot-firefox1.png')
            im2 = Image.open('working/screenshot-firefox2.png')
            get_concat_v(im1, im2).save('output/final_screenshot.png')

        else :
            driver.save_screenshot('output/final_screenshot.png')




        # Close Web Browser
        driver.quit()
