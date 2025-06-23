import json
import time
import random
from datetime import datetime, timedelta
from data import accounts
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Имитация задержки
def human_delay(min=0.5, max=1.2):
    time.sleep(random.uniform(min, max))


# ввод данных
def safe_type(element, text, driver):
    # Очистка поля через JavaScript и установка значения
    driver.execute_script("arguments[0].value = '';", element)
    for char in text:
        # Постепенный ввод с проверкой состояния
        element.send_keys(char)
        current_value = driver.execute_script("return arguments[0].value;", element)
        if not current_value.endswith(char):
            # Если символ не добавился, повторная попытка
            element.send_keys(char)
        human_delay(0.05, 0.1)


# авторизуемся на авито и переходим на страницу получения расходов
def authorisation(driver, LOGIN, PASSWORD, cab_id):
    try:
        # Навигация
        driver.get("https://www.avito.ru/")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-marker='header/login-button']"))
        ).click()

        # Ожидание стабильности формы
        form = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form[data-marker='login-form']"))
        )
        time.sleep(1)  # Дополнительная пауза для AJAX

        # Поиск элементов внутри формы
        email_input = form.find_element(By.CSS_SELECTOR, "input[name='login']")
        password_input = form.find_element(By.CSS_SELECTOR, "input[name='password']")
        submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Ввод логина
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", email_input)
        ActionChains(driver).move_to_element(email_input).pause(0.5).click().perform()
        safe_type(email_input, LOGIN, driver)

        # Ввод пароля
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", password_input)
        ActionChains(driver).move_to_element(password_input).pause(0.5).click().perform()
        safe_type(password_input, PASSWORD, driver)

        # Фиксация значений перед отправкой
        current_login = driver.execute_script("return arguments[0].value;", email_input)
        current_password = driver.execute_script("return arguments[0].value;", password_input)
        print(f"Debug: Login={current_login}, Password={current_password}")

        # Отправка формы
        ActionChains(driver).move_to_element(submit_button).pause(1).click().perform()

        # Проверка результата
        WebDriverWait(driver, 20).until(
            lambda d: "login" not in d.current_url
        )
        print("Успешная авторизация!")
        ##--------------------------------------------

        human_delay(2, 5)

        # получаем вчерашнюю дату <<<<<<<<<<<<<<<<<<<<<<<<<
        yesterday = datetime.now() - timedelta(days=1)
        data_str = yesterday.strftime("%Y-%m-%d")
        data_str = "2025-06-21"

        # проверка id кабинета
        #checkCabinetId(driver, cab_id)

        url = f"https://www.avito.ru/profile/statistics/spending?dateFrom={data_str}&dateTo={data_str}"
        driver.get(url)

        human_delay(1, 4)
        #смена кабинета
        changeCabinet(driver, cab_id)


        human_delay(1, 3)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        driver.save_screenshot('error.png')


    # формируем ссылку и переходим по ней
    url = f"https://www.avito.ru/profile/statistics/spending?dateFrom={data_str}&dateTo={data_str}"
    driver.get(url)






# получаем расходы из авито
def get_spending(driver):
    try:
        # Ждем появления хотя бы одного элемента расходов
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "₽")]'))
        )

        # Ищем все возможные варианты отображения суммы
        selectors = [
            '//div[contains(@class, "styles-spending-header")]//h3',
            '//*[contains(text(), "Итого")]/following::dd//strong',
            '//*[contains(@class, "styles-total")]//*[contains(text(), "₽")]'
        ]

        for selector in selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                amount_text = element.text.split('₽')[0].strip()
                amount = float(amount_text.replace(' ', '').replace(',', '.'))
                return int(amount)
            except:
                continue

        return None

    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
        return None


# проверка кабинета по id
def checkCabinetId(driver, cab_id):
    # проверка id кабинета

    # формируем ссылку и переходим по ней (Проверка кабинета)
    url = f"https://www.avito.ru/profile/basic"
    driver.get(url)

    # Сначала пытаемся найти старый элемент
    try:
        profile_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "p[data-marker='basic-info/user_id']")
            )
        )
        profile_text = profile_element.text.strip()
        print("Найден старый формат элемента")

    except:
        # Если не найден - ищем новый элемент
        try:
            profile_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[starts-with(., 'ID ')]")
                )
            )
            profile_text = profile_element.text.strip()
            print("Найден новый формат элемента")

        except Exception as e:
            print("Не удалось найти элемент с номером профиля")
            raise e


    # Извлекаем цифры без пробелов
    try:
        # Первый вариант: через регулярное выражение
        profile_number = re.sub(r'\D', '', profile_text)  # Удаляем все не цифры

        # Второй вариант: через split (если структура строгая)
        # profile_number = profile_text.split()[-3:]  # Берем последние 3 части
        # profile_number = ''.join(profile_number)

        if profile_number != cab_id:
            # если id кабинета не верное то меняем кабинет
            print(f"\nID {profile_number} кабинета не правельный Меняем кабинет! \n")
            changeCabinet(driver, cab_id)


        print(f"Номер профиля: {profile_number}")
    except Exception as e:
        print(f"Ошибка при обработке номера профиля: {e}")
        raise

# смена кабинета
def changeCabinet(driver, cab_id):


    # 1. Наводим курсор на аватар для открытия меню
    try:
        avatar = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@data-marker, 'header/username-button')]//img[@alt='Аватар']")
            )
        )
        # Используем ActionChains для наведения
        ActionChains(driver).move_to_element(avatar).perform()
    except Exception as e:
        print(f"Не удалось навести на аватар: {e}")
        raise

    # 2. Ждем появления пункта меню и кликаем
    try:
        menu_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@href='#profile/switch' and contains(text(), 'Мои профили')]")
            )
        )
        # Дополнительная страховка - скроллим к элементу
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", menu_item)
        menu_item.click()
    except Exception as e:
        print(f"Не удалось выбрать пункт меню: {e}")
        raise

    # Формируем CSS-селектор с использованием cab_id
    css_selector = f"div[data-marker='component-profile-switch/profile-{cab_id}']"


    try:
        # Ждем появления элемента и кликаем
        human_delay(0.5, 1)
        profile_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        # Скролим к элементу (если не виден)
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", profile_element)
        profile_element.click()
    except Exception as e:
        print(f"Ошибка при клике на профиль {cab_id}: {e}")
        # Дополнительная отладка: вывести страницу или сделать скриншот
        # driver.save_screenshot(f"profile_{cab_id}_error.png")
        raise





# получаем куки с авито
def get_cookies_in_avito(driver):
    cookies = driver.get_cookies()

    # Вывод в удобном формате
    print("Список полученных cookies:")
    # print(json.dumps(cookies, indent=2, ensure_ascii=False))

    # Формируем строку
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

    return cookie_str


# записываем в файл
def write_file(id_cab, cookie, spending):
    file_name = "data.json"

    try:
        with open(file_name, 'r', encoding="utf=8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    new_data = {
        id_cab: {
            "cabinet-name": accounts[id_cab]["name"],
            "cookies": cookie,
            "spending": spending
        }
    }

    data.append(new_data)
    with open(file_name, 'w', encoding='utf=8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)



