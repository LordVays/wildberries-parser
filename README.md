# Wildberries Parser

Парсер данных с маркетплейса Wildberries, который собирает информацию о товарах, отзывах, продажах и других данных.

## Возможности

- Сбор данных о товарах (артикулы, названия, цены, рейтинги и т.д.)
- Парсинг отзывов и вопросов о товарах
- Анализ продаж и динамики цен
- Экспорт данных в удобные форматы (CSV, JSON, Excel)

## Установка

1. Клонируйте репозиторий:
  ```bash
  git clone https://github.com/LordVays/wildberries-parser.git
  cd wildberries-parser
  ```
2. Установите зависимости:
   ```bash
   pip install selenium webdriver_manager
3. Запустите программу:
   ```bash
   python main.py
### После запуска в терминале вводите название товара и количество карточек для парсинга. 
### Данные сохраняеются в формате json в главной директории.
