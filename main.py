import time
import undetected_chromedriver as uc

from data import accounts
from helper import authorisation, get_spending, get_cookies_in_avito, write_file

# Настройки
#LOGIN = "avito.detalno.motors@fes-group.ru"
#PASSWORD = "93AvTo8024P!"

userId = input('userId\n')

# работаем со списком id разделенных пробелом
for uId in userId.split(" "):
    name = accounts[uId]['name']
    login = accounts[uId]['login']
    password = accounts[uId]['password']

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



    authorisation(driver, LOGIN, PASSWORD, uId)

    time.sleep(1)

    #input('получить куки и расход')

    cookies = get_cookies_in_avito(driver)

    spending = get_spending(driver)
    if spending == None:
        time.sleep(4)
        spending = get_spending(driver)


    print(f"cookies\n{cookies}")
    print(f"spending\n{spending}\n")

    write_file(id_cab=uId, cookie=cookies, spending=spending)

    #input('Далее')

    #spending_amount = get_spending(driver)

    #print(f"Сумма расходов: {spending_amount} ₽")


    driver.quit()
    time.sleep(1)

