import time
import undetected_chromedriver as uc

from data import accounts
from helper import authorisation, get_spending, get_cookies_in_avito

# Настройки
#LOGIN = "avito.detalno.motors@fes-group.ru"
#PASSWORD = "93AvTo8024P!"

userId = input('userId\n')

name = accounts[userId]['name']
login = accounts[userId]['login']
password = accounts[userId]['password']

print(f"имя = {name}\nлогин {login}\nпароль {password}")

LOGIN = login
PASSWORD = password

#input("stop")

try:
    print("start")

    # Настройка драйвера
    options = uc.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    print("драйвер настроен")

    # Инициализация драйвера
    driver = uc.Chrome(
        options=options,
        version_main=135,
        driver_executable_path="C:\projects\chromedriver-win64\chromedriver-win64/chromedriver.exe"
    )
    driver.set_page_load_timeout(60)
    print("драйвер инициализирован")
except Exception as e:
    print(f"Ошибка при инициализации драйвера: {str(e)}")
    driver.save_screenshot('error.png')


authorisation(driver, LOGIN, PASSWORD, userId)

time.sleep(5)
input('получить куки')

cookies = get_cookies_in_avito(driver)

print(f"cookies\n{cookies}")

input('завершить')

#spending_amount = get_spending(driver)

#print(f"Сумма расходов: {spending_amount} ₽")


time.sleep(3)
driver.quit()

