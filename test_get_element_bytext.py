# coding: utf-8

#--------------------------------------------------------------
#
#   入力されたURLのウェブページ中に指定したキーワード
#   がどの要素に存在するのかを調査するプログラム
#
#--------------------------------------------------------------

import cv2
import matplotlib.pyplot as plt
import pySaliencyMap
import numpy as np
#get screenshot
import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary #firefox使用のため
from PIL import Image #画像結合のため
#get html
import urllib
#read html
from bs4 import BeautifulSoup
import re
#use csv
import csv
import pandas as pd

# main
if __name__ == '__main__':
    # URL & File Name
    URL = input("URLを入力してください\n")
    print("ページの読み込み中...")

    binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox')
    binary.add_command_line_options('-headless')
    driver = webdriver.Firefox(firefox_binary=binary)
    driver.get(URL)

    soup = BeautifulSoup( driver.page_source, "html.parser")
    print(type(soup))

    check_words = ['Amazon','ファッション','商品']

    count = 0

    for check_word in check_words:
        count += 1
        tags = driver.find_elements_by_xpath("//*[contains(text(), '%s')]"%check_word)
        print("/"*50)
        print("調査対象%d：%s"%(count, check_word))

        i = 0

        for tag in tags:
            tag_name = tag.tag_name
            tag_id = tag.get_attribute('id')
            tag_class = tag.get_attribute('class')
            print("No.%d: <%s> id=\"%s\" class=\"%s\""%(i, tag_name, tag_id, tag_class))
            i+=1

    # Close Web Browser
    driver.quit()
