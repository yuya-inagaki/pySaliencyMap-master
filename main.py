# coding: utf-8

#--------------------------------------------------------------
#
#   Python3系で作成
#   idとclass名の取得・csvへの書き込み、該当idとclassの座標取得
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

from finalline import getFinalLine
from finalview import getHighestSaliency
from finalview import getFinalView
from finaltile import getFinalTile

screen_x = 1280
screen_y = 900

global resize_smap # リサイズ後の顕著性マップ
global width_smap # リサイズ後の顕著性マップの横幅
global height_smap # リサイズ後の顕著性マップの高さ

# 画像を二つ縦に結合する
def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

# 顕著度を計算する関数 (色平均, 重み付け後の顕著度)
def calc_salient_level(start_x, start_y, size_w, size_h, elements_name):
    if start_x < 0 :
        start_x = 0
    if start_y < 0 :
        start_y = 0
    if start_x < width and start_y < height and size_w > 0 and size_h > 0:
        end_x = int(start_x + size_w)
        end_y = int(start_y + size_h)
        if end_x > width:
            end_x = int(width)
        if end_y > height:
            end_y = int(height)
        clipped = resize_smap[int(start_y):end_y,int(start_x):end_x]
        average_color_per_row = np.average(clipped, axis=0)
        average_color = np.average(average_color_per_row, axis=0)
        average_color = np.uint8(average_color)

        # 重み付け箇所 サイズによる重み付け
        salient_level_weight = (end_x - start_x) * (end_y - start_y)
        if salient_level_weight > 1000:
            salient_level_num = average_color[0]
        elif salient_level_weight > 800:
            salient_level_num = average_color[0]*0.7
        elif salient_level_weight > 500:
            salient_level_num = average_color[0]*0.6
        else:
            salient_level_num = average_color[0]*0.2

        # 位置による重み付け
        place_weight_x = 0.1  #最低圧縮値(0~1) 0.1
        place_weight_y = 0.4  #最低圧縮値(0~1) 0.3
        center_weight = 0.2 #最低圧縮値(0~1) 0.3

        if size_w < width and size_h < height:
            topleft_bias = ( 1- ( place_weight_y - ( (height - (start_y + size_h/2) ) * place_weight_y / height ) ) ) * ( 1- ( place_weight_x - ( (width - (start_x + size_w/2) ) * place_weight_x / width ) ) )
            center_bias_x = abs( width/2 - (start_x + size_w/2) ) * abs( width/2 - (start_x + size_w/2) )
            center_bias_y = abs( height/2 - (start_y + size_h/2) ) * abs( height/2 - (start_y + size_h/2) )
            center_bias_calc = np.sqrt( center_bias_x + center_bias_y ) / np.sqrt ( width * width + height * height)

            salient_level_num = salient_level_num * ( topleft_bias - (center_weight * center_bias_calc) )

        return average_color[0], salient_level_num #平均色, 重み付け後の顕著度
    else:
        return 0, 0


# main
if __name__ == '__main__':

    global resize_smap
    global width_smap
    global height_smap

    # URL & File Name
    URL = input("URLを入力してください\n")
    print("ページの読み込み中...")

    #保存するファイル名
    FILENAME = "screen-pc.png"



    # スクリーンショットの取得
    print('Get screenshot...')
    binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox')
    binary.add_command_line_options('-headless')
    driver = webdriver.Firefox(firefox_binary=binary)
    driver.get(URL)
    window_width = 1280
    window_height = 800
    driver.set_window_size(window_width, window_height)

    soup = BeautifulSoup( driver.page_source, "html.parser")
    print(type(soup))

    page_height = driver.execute_script('return document.body.scrollHeight')
    scrollHeight = driver.execute_script('return window.innerHeight')

    print(scrollHeight)


    # ページ読み込み完了まで待機
    input("アニメーション等の読み込みが完了したらEnterを押してください\n")

    driver.save_screenshot('working/screenshot-firefox1.png')

    if page_height > scrollHeight*2 :
        driver.execute_script("window.scrollTo(0, "+str(scrollHeight)+");")
        driver.save_screenshot('working/screenshot-firefox2.png')

        im1 = Image.open('working/screenshot-firefox1.png')
        im2 = Image.open('working/screenshot-firefox2.png')
        get_concat_v(im1, im2).save('./working/screen-pc.png')

    elif page_height > scrollHeight :
        driver.execute_script("window.scrollTo(0, "+str(page_height - scrollHeight)+");")
        driver.save_screenshot('working/screenshot-firefox2.png')

        im1 = Image.open('working/screenshot-firefox1.png')
        im2 = Image.open('working/screenshot-firefox2.png')
        get_concat_v(im1, im2).save('./working/screen-pc.png')

    else :
        driver.save_screenshot('./working/screen-pc.png')


    # スクリーンショットのロード
    print('Loading screenshot...')
    img = cv2.imread('./working/screen-pc.png')

    # スクショのサイズを取得・顕著性マップの生成
    print('initialize screenshot...')
    imgsize = img.shape
    img_width  = imgsize[1] # WIDTH
    img_height = imgsize[0] # HEIGHT
    sm = pySaliencyMap.pySaliencyMap(img_width, img_height)
    # computation
    print("Calculating Saliency map...")
    saliency_map = sm.SMGetSM(img)
    print("Calculating Binarized map...")
    binarized_map = sm.SMGetBinarizedSM(img)

    # グレースケール（２値化）に変換
    print("Convert to gray scale saliency map...")
    saliency_map = saliency_map.astype(np.float64)
    saliency_map = saliency_map * 255
    saliency_map = saliency_map.astype(np.uint8)
    cv2.imwrite("./output/saliency_map.png", saliency_map ) #Save
    print("Output Complete")


    # 画像の読み込み
    img = cv2.imread("./output/saliency_map.png", 1)
    screenshot = cv2.imread("./working/screen-pc.png", 1)

    # 画像の高さ、幅を取得
    height_smap = img.shape[0]/2
    width_smap = 1280
    size = (int(width_smap), int(height_smap))
    resize_smap = cv2.resize(img, size) #顕著性マップをリサイズしたもの
    halfImg_print = cv2.resize(img, size)

    # 画像の高さ、幅を取得
    height = screenshot.shape[0]/2
    width = 1280
    size = (int(width), int(height))
    screenshot = cv2.resize(screenshot, size)


    # HTMLの保存
    print("Load and save HTML...")
    output_html = soup.prettify() #html成形
    f = open('./output/index.html', 'w') # 書き込みモードで開く
    f.write(output_html) # 引数の文字列をファイルに書き込む
    f.close() # ファイルを閉じる

    # csvの読み込み
    print("Load and create CSV file...")
    tag_list = open('./working/tag_list.csv', 'w')
    csvWriter = csv.writer(tag_list)
    csvWriter.writerow(['class or id', 'tag_name', 'start_x', 'start_y', 'size_w', 'size_h', 'average_color', 'salient_level'])
    tag_list_custom = open('./working/tag_list_custom.csv', 'w')
    csvWriter2 = csv.writer(tag_list_custom)
    csvWriter2.writerow(["class or id", "tag_name", "start_x", "start_y", "size_w", "size_h", "average_color", "salient_level"])


    # divのclassとidを取得
    print("Getting position and size of //div[@id]")
    tags_id = driver.find_elements_by_xpath("//div[@id]")
    for tag_id in tags_id:

        # print(tag_id.get_attribute('id'))
        # print(tag_id.is_displayed())
        if str(tag_id.is_displayed()) == "True": #表示されている時のみリストに挿入
            tag_id_name = tag_id.get_attribute('id')
            start_x = tag_id.location['x']
            start_y = tag_id.location['y']
            size_w = tag_id.size['width']
            size_h = tag_id.size['height']

            saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'tag_id') #顕著度の計算

            if (size_w * size_h) > (screen_x * 800 / 3):
                #サイズが大きいものの名前を変更
                csvWriter.writerow(["id_large", tag_id_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
            else:
                csvWriter.writerow(["id", tag_id_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["id", tag_id_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])


    print("Getting position and size of //div[@class]")
    tags_class = driver.find_elements_by_xpath('//div[@class]')
    for tag_class in tags_class:
        try: # 正常処理
            # print(tag_class.get_attribute('class'))
            # print(tag_class.is_displayed())
            if str(tag_class.is_displayed()) == "True": #表示されている時のみリストに挿入
                tag_class_name = tag_class.get_attribute('class')
                start_x = tag_class.location['x']
                start_y = tag_class.location['y']
                size_w = tag_class.size['width']
                size_h = tag_class.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'tag_class') #顕著度の計算

                if (size_w * size_h) > (screen_x * 800 / 3):
                    #サイズが大きいものの名前を変更
                    csvWriter.writerow(["class_large", tag_class_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])

                else:
                    csvWriter.writerow(["class", tag_class_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                    #顕著度が存在するもののみ
                    if saliency_level[1] > 0:
                        csvWriter2.writerow(["class", tag_class_name, start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])

        except: # エラー処理
            print("Error(Can't find elements[class]) ->" + tag_class.get_attribute('class'))


    print("Getting position and size of //h1")
    tags_h1 = driver.find_elements_by_xpath('//h1')
    for tag_h1 in tags_h1:
        try: # 正常処理
            # print(tag_img.is_displayed())
            if str(tag_h1.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = tag_h1.location['x']
                start_y = tag_h1.location['y']
                size_w = tag_h1.size['width']
                size_h = tag_h1.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'h1') #顕著度の計算

                csvWriter.writerow(["heading", "h1", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["heading", "h1", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
        except: # エラー処理
            print("Error(Can't find elements[h1])")

    print("Getting position and size of //h2")
    tags_h2 = driver.find_elements_by_xpath('//h2')
    for tag_h2 in tags_h2:
        try: # 正常処理
            if str(tag_h2.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = tag_h2.location['x']
                start_y = tag_h2.location['y']
                size_w = tag_h2.size['width']
                size_h = tag_h2.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'h2') #顕著度の計算

                csvWriter.writerow(["heading", "h2", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["heading", "h2", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
        except: # エラー処理
            print("Error(Can't find elements[h2])")

    print("Getting position and size of //h3")
    tags_h3 = driver.find_elements_by_xpath('//h3')
    for tag_h3 in tags_h3:
        try: # 正常処理
            if str(tag_h3.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = tag_h3.location['x']
                start_y = tag_h3.location['y']
                size_w = tag_h3.size['width']
                size_h = tag_h3.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'h3') #顕著度の計算

                csvWriter.writerow(["heading", "h3", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["heading", "h3", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
        except: # エラー処理
            print("Error(Can't find elements[h3])")


    print("Getting position and size of //a")
    tags_link = driver.find_elements_by_xpath('//a')
    for tag_link in tags_link:
        try: # 正常処理
            # print(tag_link.is_displayed())
            try:
                tag_link.find_element_by_tag_name('img') #リンク内部に画像が含まれるものは除外
            except:
                # print('画像なし！')
                if str(tag_link.is_displayed()) == "True": #表示されている時のみリストに挿入
                    start_x = tag_link.location['x']
                    start_y = tag_link.location['y']
                    size_w = tag_link.size['width']
                    size_h = tag_link.size['height']

                    saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'link') #顕著度の計算

                    csvWriter.writerow(["a", "link", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                    #顕著度が存在するもののみ
                    if saliency_level[1] > 0:
                        csvWriter2.writerow(["a", "link", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])

        except: # エラー処理
            print("Error(Can't find elements[link])")

    print("Getting position and size of //span")
    tags_span = driver.find_elements_by_xpath('//span')
    for tag_span in tags_span:
        try: # 正常処理
            # print(tag_span.is_displayed())
            if str(tag_span.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = tag_span.location['x']
                start_y = tag_span.location['y']
                size_w = tag_span.size['width']
                size_h = tag_span.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'span') #顕著度の計算

                csvWriter.writerow(["span", "span", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["span", "span", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])

        except: # エラー処理
            print("Error(Can't find elements[img])")

    print("Getting position and size of //img")
    tags_img = driver.find_elements_by_xpath('//img')
    for tag_img in tags_img:
        try: # 正常処理
            # print(tag_img.is_displayed())
            if str(tag_img.is_displayed()) == "True": #表示されている時のみリストに挿入
                start_x = tag_img.location['x']
                start_y = tag_img.location['y']
                size_w = tag_img.size['width']
                size_h = tag_img.size['height']

                saliency_level = calc_salient_level(start_x, start_y, size_w, size_h, 'img') #顕著度の計算

                csvWriter.writerow(["img", "image", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
                #顕著度が存在するもののみ
                if saliency_level[1] > 0:
                    csvWriter2.writerow(["img", "image", start_x, start_y, size_w, size_h, saliency_level[0], saliency_level[1]])
        except: # エラー処理
            print("Error(Can't find elements[img])")



    tag_list.close() # csv_file close()
    tag_list_custom.close()

    # Close Web Browser
    driver.quit()


    getFinalLine()
    getHighestSaliency()
    getFinalView()
    getFinalTile()
