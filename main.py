from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from chatGPT import run_openai_chat
import emoji
import json
import re
import time

def has_emoji(sentence):
  for char in sentence:
    if emoji.is_emoji(char):
      return True
  return False

def clean_sentences(input_string):
    # Loại bỏ kí hiệu không mong muốn
    input_string = input_string.replace('"', '').replace("'", "").replace(".", "").replace("(", "").replace(")", "").replace(":", "")
    # Chia chuỗi dựa vào dấu xuống dòng
    sentences = input_string.split("\n")

    # Lấy ra từng câu bỏ qua số thứ tự chỉ khi dòng bắt đầu bằng số
    cleaned_sentences = []
    for sentence in sentences:
        first_word = sentence.split(" ", 1)[0]
        if first_word.isdigit() and "cảm xúc" not in sentence.lower():
            cleaned_sentences.append(sentence.split(" ", 1)[-1])

    return [sentence for sentence in cleaned_sentences if has_emoji(sentence)]

def click_heart(driver):
    # Hover and click the heart
    element_to_hover = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "reactinText_fe9327d3")))
    element_to_hover.location_once_scrolled_into_view
    hover = ActionChains(driver).move_to_element(element_to_hover)
    hover.perform()

    # Wait for the heart to be clickable
    hover_box_heart = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='ant-popover-inner-content']/div[1]/div[2]")))

    # print("Performing heart-clicking action.")
    hover_box_heart.click()

def shorten_content(text, num):
    # Thay thế các dãy khoảng trắng liên tiếp bằng một khoảng trắng duy nhất
    single_spaced = re.sub(r'\s+', ' ', text)

    # Tách chuỗi thành danh sách các từ
    words = single_spaced.split(' ')

    # Lấy 150 từ đầu tiên
    content = words[:num]

    # Nối lại để tạo chuỗi và trả về kết quả
    return ' '.join(content)

def extract_link(account, idx, lst_cmt, news_num):
    driver.get("https://tngholding.sharepoint.com/sites/tconnect/SitePages/NewsListing.aspx?cateId=25")

    # Find the search box
    username_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginfmt'][type='email']")))
    username_box.send_keys(account['username'])
    username_box.send_keys(Keys.RETURN)

    time.sleep(5)
    password_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='passwd'][type='password']")))
    password_box.send_keys(account['password'])
    password_box.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".win-button.button-secondary.button.ext-button.secondary.ext-secondary"))).click()
    print(f"{account['username']} đã đăng nhập thành công")

    img_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "imgWidth_b8a20ea4")))
    # Check if at least two elements were found
    if len(img_elements) >= 2:
        img_src = img_elements[news_num].get_attribute('src')
        match = re.search(r'\/(\d+)\/', img_src)
        if match:
            extracted_string = match.group(1)
        else:
            print("Không tìm thấy chuỗi cần trích xuất.")
    else:
        print("Không tìm thấy đủ số lượng các phần tử có class 'imgWidth_b8a20ea4' trên trang.")

    link_news = f'https://tngholding.sharepoint.com/sites/tconnect/SitePages/NewsDetail.aspx?cateId=25&nid={extracted_string}'
    print(f"link báo đã được lấy thành công: {link_news}")
    driver.get(link_news)

    # Check if the element exists
    love_emoji = None
    try:
        love_emoji = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".zama-emoji.emoji--love.xs")))
    except TimeoutException:
        pass
    if love_emoji is None:
        click_heart(driver)
        print(f"{account['username']} thả tim")
    else:
        print(f"{account['username']} đã thả tim trước đó")

    title = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'titleNews_1dbcc9f3')))
    content_title = title.text
    description = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'shortdescription_1dbcc9f3')))
    content_description = description.text
    content_paragraphs = ''
    paragraphs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='newDetails_1dbcc9f3']/div[4]/div[1]/div[1]")))
    for i in paragraphs:
        content_paragraphs += i.text
    content_news = content_title + content_description + content_paragraphs
    content_news_short = shorten_content(content_news, 200)
    while len(lst_cmt) != len(accounts):
        cmt = run_openai_chat(content_news_short, len(accounts))
        lst_cmt = clean_sentences(cmt)

    username_box = wait.until(EC.presence_of_element_located((By.ID, "autoresizing")))
    driver.execute_script("arguments[0].scrollIntoView();", username_box)
    username_box.send_keys(lst_cmt[idx])
    driver.find_element(By.CSS_SELECTOR, '.ant-btn.ant-btn-primary.ant-btn-round').click()
    print(f"{account['username']} đã bình luận thành công: '{lst_cmt[idx]}'")
    time.sleep(5)
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.delete_all_cookies()
    return link_news, lst_cmt

def no_extract_link(account, idx, lst_cmt):
    driver.get(link_news)

    # Find the search box
    username_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loginfmt'][type='email']")))
    username_box.send_keys(account['username'])
    username_box.send_keys(Keys.RETURN)

    time.sleep(5)
    password_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='passwd'][type='password']")))
    password_box.send_keys(account['password'])
    password_box.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".win-button.button-secondary.button.ext-button.secondary.ext-secondary"))).click()
    print(f"{account['username']} đã đăng nhập thành công")

    # Check if the element exists
    love_emoji = None
    try:
        love_emoji = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".zama-emoji.emoji--love.xs")))
    except TimeoutException:
        pass
    if love_emoji is None:
        click_heart(driver)
        print(f"{account['username']} thả tim")
    else:
        print(f"{account['username']} đã thả tim trước đó")

    username_box = wait.until(EC.presence_of_element_located((By.ID, "autoresizing")))
    driver.execute_script("arguments[0].scrollIntoView();", username_box)
    username_box.send_keys(lst_cmt[idx])
    driver.find_element(By.CSS_SELECTOR, '.ant-btn.ant-btn-primary.ant-btn-round').click()
    print(f"{account['username']} đã bình luận thành công: '{lst_cmt[idx]}'")
    time.sleep(5)

with open('account.json', 'r') as file:
    accounts = json.load(file)['account']

link_news = None
lst_cmt = []
for idx, account in enumerate(accounts):
    if link_news is None and lst_cmt == []:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, 30)
        link_news, lst_cmt_temp = extract_link(account, idx, lst_cmt, 2)
        lst_cmt.extend(lst_cmt_temp)
        driver.quit()
        print("==================================================================================================")
    else:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, 30)
        no_extract_link(account, idx, lst_cmt)
        driver.quit()
        print("==================================================================================================")
print("kết thúc chương trình")

driver.quit()