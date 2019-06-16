# coding: utf-8
#--------------------------------------------------------------
#
#   入力されたURLのウェブページ中の名刺と一般を取り出し
#   それぞれの単語の出現数を多い順に返すプログラム
#
#--------------------------------------------------------------




import MeCab
import re
from collections import Counter

import requests #HTML取得
from bs4 import BeautifulSoup #HTML整形



# main
if __name__ == '__main__':
    # URL & File Name
    URL = input("URLを入力してください\n")

    ##HTML取得・整形
    html=requests.get(URL).text
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
    print(counter)

    for word, count in counter.most_common(): ##counter.most_common で出現頻度が高い順に取得
        print(f"{word}: {count}")
