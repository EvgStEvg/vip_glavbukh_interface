# VIP Glavbukh Interface

Веб-приложение для Бухгалтерии

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv new_vip_env
   source new_vip_env/bin/activate  # для Linux/Mac
   new_vip_env\Scripts\activate     # для Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Скопируйте `.env.example` в `.env` и заполните своими данными
5. Запустите приложение:
   ```bash
   python app.py
   ```

## Структура проекта
vip_glavbukh_interface/
├── blueprints/
│ ├── auth/
│ ├── consultations/
│ ├── main/
│ └── consulting_platforms/
├── static/
├── templates/
├── app.py
├── config.py
└── models.py

