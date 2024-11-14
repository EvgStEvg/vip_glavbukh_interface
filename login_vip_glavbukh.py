import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, TimeoutException
from selenium.webdriver.common.alert import Alert
import time

# Credentials
vip_username = sys.argv[1] if len(sys.argv) > 1 else "your_username"
vip_password = sys.argv[2] if len(sys.argv) > 2 else "your_password"

# Initialize the browser
driver = webdriver.Chrome()
driver.get("https://buh.action360.ru/?from=id2cabinet")

try:
    print("Ищем и нажимаем кнопку 'Вход и регистрация'...")
    time.sleep(2)  # Wait before searching for the login button
    login_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Вход и регистрация']"))
    )
    login_button.click()

    time.sleep(2)  # Wait before switching windows
    print("Переключаемся на окно формы входа...")
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)

    print("Ожидание загрузки формы входа...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "login"))
    )
    
    time.sleep(2)  # Simulate user pause
    print(f"Вводим логин: {vip_username}")
    email_input = driver.find_element(By.NAME, "login")
    email_input.send_keys(vip_username)

    time.sleep(2)  # Simulate user pause
    print(f"Вводим пароль: {vip_password}")
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(vip_password)

    time.sleep(2)  # Simulate user pause
    print("Нажимаем на кнопку 'Войти'...")
    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
    submit_button.click()

    # Handle the pop-up for notifications if it appears
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = Alert(driver)
        alert.dismiss()  # or alert.accept() depending on what you want to do
        print("Закрыли всплывающее окно с уведомлением.")
    except (NoSuchWindowException, NoSuchElementException, TimeoutException):
        print("Всплывающее окно не обнаружено или не удалось обработать.")

    print("Ждем перехода на основную страницу...")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "search-text")))

    print("Переход на основную страницу выполнен успешно. Переходим к поисковому полю...")
    
    search_input = driver.find_element(By.ID, "search-text")
    search_input.send_keys("Ваш запрос")

    print("Поиск выполнен. Запрос отправлен.")
    
    # Optionally, take a screenshot after the operation
    driver.save_screenshot('screenshot_final.png')

except NoSuchWindowException as e:
    print("Окно было закрыто раньше времени:", e)
except TimeoutException as e:
    print("Превышено время ожидания:", e)
except Exception as e:
    print(f"Произошла непредвиденная ошибка: {e}")
finally:
    print("Закрываем браузер.")
    driver.quit()
