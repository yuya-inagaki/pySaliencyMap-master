

・seleniumのインストール
pip install selenium

・geckodriverのダウンロードと解凍と配置
[DL-link] https://github.com/mozilla/geckodriver/releases
解凍後に以下の場所に配置
[配置場所] /usr/local/bin/

・Beautiful Soup4のインストール（HTMLの解析のため）
pip install beautifulsoup4


【今後の手順】2018/11/9
・urlからスクリーンショットの取得（20181022完了）
・取得したスクリーンショットから顕著性マップの取得と表示（20181029完了）
・顕著性マップのローカル環境への保存（20181029完了）
・urlからHTMLの取得（20181109完了）
・取得したHTMLの各div要素の位置をスクレイピングしてCSSまたはJavaScriptから取得する（20181210完了）
・取得した位置の範囲内の顕著度合いを顕著性マップとの比較から取得（20181210完了）
・各要素の顕著度を取得できる！