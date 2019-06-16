# coding: utf-8

#--------------------------------------------------------------
#
#   入力されたURLのウェブページ中に指定したキーワード
#   がどの要素に存在するのかを調査するプログラム
#
#--------------------------------------------------------------

# ウェブスクレイピング・HTML取得に使用
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary #firefox使用のため
from bs4 import BeautifulSoup
import requests #HTML取得

# 形態素解析に使用
import MeCab
import re
from collections import Counter


# 特定のワードを受け取りそのワードが含まれている要素を返す関数(チェックするワード, driver)
def get_element_byword(check_word, driver):
    tags = driver.find_elements_by_xpath("//*[contains(text(), '%s')]"%check_word)
    return tags

# URLを受け取り出現単語を出現数が多い単語順に並び替えて辞書型で出力する関数(url)
def get_frequent_words(url):
    ##HTML取得・整形
    html=requests.get(url).text
    soup=BeautifulSoup(html,"html.parser")

    ##scriptやstyleを含む要素を削除する
    for script in soup(["script", "style"]):
        script.decompose()

    ##テキストのみを取得=タグは全部取る
    text=soup.get_text()

    ##textを改行ごとにリストに入れて、リスト内の要素の前後の空白を削除
    lines= [line.strip() for line in text.splitlines()]

    ##リストの空白要素以外をすべて文字列に戻す
    data="".join(line for line in lines if line)

    # パース
    mecab = MeCab.Tagger()
    parse = mecab.parse(data)
    lines = parse.split('\n')
    items = (re.split('[\t,]', line) for line in lines)

    # 名詞をリストに格納
    words = [item[0]
             for item in items
             if (item[0] not in ('EOS', '', 't', 'ー') and
                 item[1] == '名詞' and item[2] == '一般')]

    # 頻度順に出力
    counter = Counter(words)
    return counter




# main
if __name__ == '__main__':

    # URL & File Name
    URL = input("URLを入力してください\n")
    print("ページの読み込み中...")
    binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox')
    binary.add_command_line_options('-headless')
    driver = webdriver.Firefox(firefox_binary=binary)
    driver.get(URL)

    words = get_frequent_words(URL)
    i = 0
    for word, count in words.most_common(): ##most_common関数で出現頻度が高い順に取得
        if i>=3: break
        i+=1

        print("/"*50)
        print("調査対象：%s (%d個)"%(word, count))

        tags = get_element_byword(word, driver)

        j = 0
        for tag in tags:
            tag_name = tag.tag_name
            tag_id = tag.get_attribute('id')
            tag_class = tag.get_attribute('class')
            print("No.%d: <%s> id=\"%s\" class=\"%s\""%(j, tag_name, tag_id, tag_class))
            j+=1

    # Close Web Browser
    driver.quit()
