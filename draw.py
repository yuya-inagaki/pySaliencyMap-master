
import cv2
import pandas as pd

## 頻出単語の描写を行う関数
def draw_frequent_word():

    ## 画像の読み込み
    img = cv2.imread("./working/screen-pc.png", 1)

    ## 画像の高さ、幅を取得
    height = img.shape[0]/2
    width = 1280
    size = (int(width), int(height))
    halfImg = cv2.resize(img, size)

    # csvの読み込み
    tag_list_num = sum(1 for line in open('./working/tag_list_freq_word.csv'))
    print(tag_list_num)

    tag_list = pd.read_csv('./working/tag_list_freq_word.csv')
    print(tag_list)

    for i in reversed(range(tag_list_num - 1)):
        print(i)
        start_x = int(tag_list.iat[i, 2])
        start_y = int(tag_list.iat[i, 3])
        end_x = int(tag_list.iat[i, 2]+tag_list.iat[i, 4])
        end_y = int(tag_list.iat[i, 3]+tag_list.iat[i, 5])

        print(start_x, start_y, end_x, end_y)

        if tag_list.iat[i, 1] == 1:
            cv2.rectangle(halfImg, (start_x, start_y) , (end_x, end_y), (0, 0, 255), 3) # 赤色
        elif tag_list.iat[i, 1] == 2:
            cv2.rectangle(halfImg, (start_x, start_y) , (end_x, end_y), (0, 255, 0), 3) # 赤色
        elif tag_list.iat[i, 1] == 3:
            cv2.rectangle(halfImg, (start_x, start_y) , (end_x, end_y), (255, 0, 0), 3) # 赤色


    # 画像を表示
    cv2.namedWindow("halfImg", cv2.WINDOW_NORMAL)
    cv2.imshow("halfImg", halfImg)
    cv2.imwrite("./output/final_freq_word.png", halfImg ) #Save
    k = cv2.waitKey(0)
    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()
