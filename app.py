import os
import time
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def run_selenium_script(email, password):
    # متغير لتخزين بيانات الاعتماد
    credentials_dict = {}

    # إعداد مجلد لتخزين الملف النصي (اختياري لتخزين البيانات)
    credentials_dir = os.path.join(os.getcwd(), 'cridintial')
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    # إعداد خيارات متصفح Chrome
    chrome_options = Options()
    prefs = {
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # تشغيل المتصفح بدون واجهة رسومية مع إضافة خيارات إضافية لبيئة replit
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # تحديد موقع Chromium في replit
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    # استخدام Service مع webdriver-manager لتحديد chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    try:
        # الانتقال إلى صفحة تسجيل الدخول
        driver.get("https://profile.eta.gov.eg/TaxpayerProfile")

        # إدخال البريد الإلكتروني
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(email)

        # إدخال كلمة المرور
        driver.find_element(By.ID, "Password").send_keys(password)

        # النقر على زر تسجيل الدخول
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)

        # محاولة الضغط على زر "Select" إن وجد
        try:
            form_group = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.form-group"))
            )
            select_button = form_group.find_element(By.XPATH, "//*[normalize-space(text())='Select']")
            select_button.click()
            print("تم الضغط على زر Select.")
            time.sleep(2)
        except Exception as e:
            print("زر Select غير موجود، متابعة التنفيذ.")

        # تنفيذ باقي خطوات العملية
        try:
            erp_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, "ERP "))
            )
            erp_button.click()
            print("تم النقر على زر ERP بنجاح.")
            time.sleep(3)

            add_icon = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-icon-name="Add"]'))
            )
            add_icon.click()
            print("تم النقر على أيقونة Add بنجاح.")
            time.sleep(3)

            friendly_name_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[placeholder="Create a friendly name for the ERP system "]'))
            )
            friendly_name_input.clear()
            friendly_name_input.send_keys("Mohasib Friend")
            print("تم تعبئة حقل الإدخال بالكلمة 'Mohasib Friend' بنجاح.")
            time.sleep(3)

            register_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Register']"))
            )
            register_button.click()
            print("تم النقر على زر Register بنجاح.")
            time.sleep(5)

            # الحصول على بيانات الاعتماد بعد التسجيل
            credential_containers = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.vertialFlexDiv"))
            )

            for container in credential_containers:
                try:
                    label = container.find_element(By.CSS_SELECTOR, "label.ms-Label").text.strip()
                    input_value = container.find_element(By.CSS_SELECTOR, "input.ms-TextField-field").get_attribute("value").strip()
                    credentials_dict[label] = input_value
                    print(f"تم التقاط {label}: {input_value}")
                except Exception as e:
                    print("حدث خطأ أثناء استخراج البيانات:", e)

            # حفظ البيانات في ملف نصي (اختياري)
            reg_number = credentials_dict.get("Registration Number", "credentials")
            Client_ID = credentials_dict.get("Client ID", "credentials")
            Client_Secret_1 = credentials_dict.get("Client Secret 1", "credentials")
            output_file_name = f"{reg_number},{Client_ID},{Client_Secret_1}.txt"
            output_file_path = os.path.join(credentials_dir, output_file_name)
            with open(output_file_path, "w", encoding="utf-8") as file:
                for key, value in credentials_dict.items():
                    file.write(f"{key}: {value}\n")
            print("تم حفظ بيانات الاعتماد في الملف:", output_file_path)
            time.sleep(3)

        except Exception as e:
            print("حدث خطأ أثناء تنفيذ باقي الخطوات:", e)

    finally:
        driver.quit()
        return credentials_dict

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    email = request.form.get('email')
    password = request.form.get('password')
    credentials = run_selenium_script(email, password)
    return render_template('result.html', credentials=credentials)

if __name__ == '__main__':
    # تشغيل الخادم ليستمع لجميع الاتصالات على المنفذ 8000
    app.run(debug=True, host='0.0.0.0', port=8000)
