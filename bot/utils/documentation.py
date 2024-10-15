documentation_ru = """

1. **Подготовка к установке**
   * Убедитесь, что у вас установлен **`Python 3.10`** | Инструкция по установке Python (https://www.python.org/downloads/)
   * Скачайте и распакуйте архив либо используйте команду `git clone [URL РЕПОЗИТОРИЯ]`
   * Перейдите в папку скрипта: `cd your_script_folder`

2. **Создайте и активируйте виртуальное окружение**
    * Windows: `python -m venv venv` и `venv/Scripts/activate`
    * Linux: `python3.10 -m venv venv` и `source venv/bin/activate` 

3. **Установка зависимостей**
    * Установите зависимости, используя команду: `pip install -r requirements.txt`

4. **Создаем и заполняем `.env` файл**
    * Введите в терминале: 
        * Windows: `copy .env-example .env`.
        * Linux: `cp .env-example .env`.

5. **Получаем API ключи**   
   * Переходим на сайт [`https://my.telegram.org`](#) и авторизуемся используя свой номер телефона.
   * Выбираем **"API development tools"** и заполняем форму создания нового приложения.
   * Записываем полученные `API_ID` и `API_HASH` в `.env` файл.

6. **Настраиваем прокси**
    1. Заполните файл `session_proxy.json`, привязав каждый аккаунт к отдельному прокси.
    2. Для автоматического заполнения:
         * Добавьте все ваши прокси в файл `proxies.txt` и назовите ваши сессии, к примеру "1-Andrey", "2-John". Если назовете сессии иначе, скрипт рандомно получит прокси для каждой сессии.
         * В терминале выполните команду ` python bot/config/proxies/session_proxy_matcher.py`
         * Скрипт сопоставит каждую строку прокси с номером аккаунта и добавит их в файл `session_proxy.json`. Таким образом вы получите готовый файл, где первая строка прокси будет соответствовать первому аккаунту, и так далее.

7. **Создание сессий либо использование готовых**
    * Для использования готовых сессий pyrogram добавьте их в папку sessions
    * Для создания новых сессий выполните команду `python main.py`
    * Выберите опцию 2 в главное меню программы и следуйте инструкциям на экране.

8. **Запуск скрипта**
    * Выполните команду `python main.py` и выберите опцию "1" в главном меню, скрипт начнет работу.


> ⚠️  **ВНИМАНИЕ**:
> - Используйте уникальные прокси для каждой сессии
> - Не злоупотребляйте скриптом во избежание блокировок
> - Соблюдайте осторожность и правила использования

Нужна помощь? Ссылка на наше комьюнити [`https://t.me/web3community_ru`](#)

---

**Отказ от ответственности:** _Используйте скрипт на свой страх и риск. Автор этого скрипта не несет ответственности за любые действия пользователей и их последствия, включая блокировку аккаунтов и другие ограничения. Мы рекомендуем вам быть осторожными и избегать передачи конфиденциальной информации, так как это может привести к компрометации ваших данных. Перед использованием обязательно ознакомьтесь с условиями обслуживания приложений, с которыми вы работаете, чтобы избежать нарушения их правил. Учитывайте, что автоматизация может вызвать нежелательные последствия, такие как временная или полная блокировка вашего аккаунта. Всегда действуйте осознанно и учитывайте возможные риски._
"""

documentation_en = """

1. **Preparation for Installation**
   * Ensure that **`Python 3.10`** is installed | Installation instructions for Python (https://www.python.org/downloads/)
   * Download and extract the archive or use the command `git clone [REPOSITORY URL]`.
   * Navigate to the script folder: `cd your_script_folder`

2. **Create and Activate a Virtual Environment**
   * Windows: `python -m venv venv` and `venv/Scripts/activate`
   * Linux: `python3.10 -m venv venv` and `source venv/bin/activate`

3. **Install Dependencies**
   * Install dependencies using the command: `pip install -r requirements.txt`.

4. **Create and Fill the `.env` File**
   * Enter the command in the terminal: 
   * Windows: `copy .env-example .env`.
   * Linux: `cp .env-example .env`.

5. **Obtaining API Keys**   
   * Go to [`https://my.telegram.org`](#) and log in using your phone number.
   * Select **"API development tools"** and fill out the form to register a new application.
   * Record the `API_ID` and `API_HASH` in the `.env` file, provided after registering your application.

6. **Configure Proxy**
   1. Fill in the `session_proxy.json` file, linking each account to a separate proxy.
   2. For automatic filling:
      * Add all your proxies to the `proxies.txt` file in format `http://login:password@ip:port` and name your sessions in folder sessions, for example, "1-Andrey", "2-John". If you name the sessions differently, the script will randomly get a proxy for each session.
      * In the terminal, run the command: ` python bot/config/proxies/session_proxy_matcher.py`.
      * The script will match each proxy line with the account number and add them to the `session_proxy.json` file. This way, you will have a ready-made file where the first proxy line corresponds to the first account, and so on.

7. **Create Sessions or Use Existing Ones**
   * To use existing pyrogram sessions, add them to the `sessions` folder.
   * To create new sessions, run in terminal: `python main.py`
   * Select option "2" in the main menu of the program and follow the prompts 

8. **Run the Script**
   * Run in terminal: `python main.py` and select option "1" in the main menu, and the script will start running.


> ⚠️  **WARNING**:
> - Use unique proxies for each session
> - Do not abuse the script to avoid blockages
> - Exercise caution and follow usage guidelines

Need some help? Our community link [`https://t.me/web3community_ru`](#)

---

**Disclaimer:** _Use the script at your own risk. The author of this script is not responsible for any actions taken by users and their consequences, including account bans and other restrictions. We recommend that you exercise caution and avoid sharing confidential information, as this may lead to the compromise of your data. Before using, be sure to review the terms of service of the applications you are working with to avoid violating their rules. Keep in mind that automation may result in unwanted consequences, such as temporary or permanent suspension of your account. Always act consciously and consider the potential risks._
"""


def get_documentation(language='ru'):
    return documentation_ru if language == 'ru' else documentation_en