
from PIL import Image #画像結合のため

# 画像を二つ縦に結合する関数(image1, image2)
def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_screenshot(driver):
    window_width = 1280
    window_height = 800
    driver.set_window_size(window_width, window_height)

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
