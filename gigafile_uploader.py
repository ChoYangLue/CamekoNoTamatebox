"""
pip install selenium tqdm
pip install chromedriver-binary
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time, sys, os
from pathlib import Path


def upload_files(file_paths, lifetime=100):
    # Chromeオプションの設定
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument("--headless")  # ヘッドレスモードを有効化

    # WebDriverの設定
    driver = webdriver.Chrome(options=options)

    # GigaFile便のウェブサイトにアクセス
    driver.get("https://gigafile.nu/")

    # 保存期限の値に基づいて適切な要素を選択し、クリック
    valid_lifetimes = [3, 5, 7, 14, 30, 60, 100]
    if lifetime in valid_lifetimes:
        lifetime_selector = f"li[data-lifetime-val='{lifetime}']"
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, lifetime_selector)))

        # JavaScriptを使用してクリックする
        driver.execute_script("arguments[0].click();", element)
    else:
        print(f"無効な保存期限: {lifetime}。有効な値: {valid_lifetimes}")

    # ファイル選択とアップロードの処理
    file_input = driver.find_element(By.CSS_SELECTOR, "#upload_panel_button > input")
    file_input.send_keys("\n".join(file_paths))

    # Initialize tqdm progress bar
    progress_bar = tqdm(total=100, desc="Overall Progress", unit="%")

    while True:
        progress_texts = []
        for i in range(len(file_paths)):
            progress_texts.append(driver.find_element(By.CSS_SELECTOR, f"#file_{i} > div.file_info_prog_box > span").text)
        
        if all(text == "完了！" for text in progress_texts):
            progress_bar.n = 100
            progress_bar.update(0)
            break

        overall_progress = 0
        for text in progress_texts:
            if text != "完了！":
                overall_progress += int(text.rstrip("%"))
        
        overall_progress /= len(file_paths)
        progress_bar.n = overall_progress
        progress_bar.update(0)

        time.sleep(1)

    progress_bar.close()

    # .zipの名前決定
    zip_file_name = driver.find_element(By.ID,"zip_file_name")
    p_file = Path(file_paths[0])
    print(p_file.parent.name)
    zip_file_name.send_keys(p_file.parent.name)

    # 「まとめてダウンロード」リンクのURLを取得してクリック
    matomete_link_btn = driver.find_element(By.ID, "matomete_btn")
    driver.execute_script("arguments[0].click();", matomete_link_btn)

    # アラートが表示されたら、OKをクリックして閉じる
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')

        alert = driver.switch_to.alert
        alert.accept()
        print("close arert")
    except TimeoutException:
        print("not displayed arert")
    
    matomete_url_element = driver.find_element(By.ID, "matomete_url")
    origin_value = matomete_url_element.get_attribute("origin")

    # 終了時にブラウザを閉じる
    driver.quit()

    print("------------")
    print(p_file.parent.name)
    print(origin_value)
    #print("file name: "+str(p_file.parent.name))
    #print("URL:"+str(origin_value))
    #print("Delkey:"+str(delkey_origin_value))
    
    #URLを返す
    return origin_value

def main():
    args = sys.argv

    dir_path = ""
    if len(args) == 0:
        dir_path = input("file path:")
    else:
        print(args[1])
        dir_path = args[1]

    if os.path.isdir(dir_path) != True:
        input(str(dir_path)+" is not directory or not exist")
        return

    # アップロードするファイルのパスをリストに格納
    abs_path = os.path.abspath('.')
    path = os.path.join(abs_path, dir_path)
    files = os.listdir(path)
    file_paths = [os.path.join(path, file) for file in files if os.path.isfile(os.path.join(path, file))]
    print(file_paths)

    # 関数を呼び出し、ファイルのアップロードと保存期限の設定を行う
    retry_count = 0
    while(retry_count < 5):
        try:
            url = upload_files(file_paths, lifetime=100)
        except Exception as e:
            print("retry count="+str(retry_count))
            retry_count += 1
            continue
        break
            
    input()

main()
