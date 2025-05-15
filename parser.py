import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
from webdriver_manager.chrome import ChromeDriverManager

class WildberriesParser:
    def __init__(self):
        # Настройка Selenium WebDriver
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Автоматическая загрузка chromedriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        self.wait = WebDriverWait(self.driver, 20)  # Увеличили время ожидания
        self.actions = ActionChains(self.driver)
    
    def human_like_delay(self):
        """Имитация человеческой задержки"""
        time.sleep(random.uniform(0.5, 2.5))
    
    def human_like_scroll(self):
        """Имитация человеческой прокрутки"""
        scroll_amount = random.randint(300, 800)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.human_like_delay()
    
    def search_products(self, query, max_products=50):
        """Поиск товаров по запросу"""
        try:
            # Открываем сайт Wildberries
            self.driver.get("https://www.wildberries.ru/")
            self.human_like_delay()
            
            # Находим и закрываем рекламный баннер, если он есть
            try:
                close_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.popup__close")))
                close_btn.click()
                self.human_like_delay()
            except:
                pass
            
            # Находим поисковую строку (новый селектор)
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-catalog__input")))
            
            # Очищаем поле поиска
            search_box.clear()
            self.human_like_delay()
            
            # Имитируем ввод запроса
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            self.human_like_delay()
            search_box.send_keys(Keys.RETURN)
            self.human_like_delay()
            
            # Ждем загрузки результатов поиска
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-card__wrapper")))
            
            # Прокручиваем страницу для загрузки товаров
            products = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            attempts = 0
            
            while len(products) < max_products and attempts < 5:
                # Прокрутка вниз
                for _ in range(3):
                    self.human_like_scroll()
                
                # Обновляем высоту страницы после прокрутки
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    attempts += 1
                last_height = new_height
                
                # Собираем товары (новые селекторы)
                product_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product-card")))
                
                for card in product_cards[len(products):max_products]:
                    try:
                        # Прокручиваем к карточке товара
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                        self.human_like_delay()
                        
                        # Получаем информацию о товаре
                        product = {}
                        
                        # Название товара
                        try:
                            name = card.find_element(By.CSS_SELECTOR, "span.product-card__name").text
                            product['name'] = name.strip()
                        except:
                            try:
                                name = card.find_element(By.CSS_SELECTOR, "p.product-card__name").text
                                product['name'] = name.strip()
                            except:
                                product['name'] = None
                        
                        # Бренд
                        try:
                            brand = card.find_element(By.CSS_SELECTOR, "span.product-card__brand").text
                            product['brand'] = brand.strip()
                        except:
                            try:
                                brand = card.find_element(By.CSS_SELECTOR, "p.product-card__brand").text
                                product['brand'] = brand.strip()
                            except:
                                product['brand'] = None
                        
                        # Цена
                        try:
                            price = card.find_element(By.CSS_SELECTOR, "ins.price__lower-price").text
                            product['price'] = price.replace('₽', '').replace(' ', '').strip()
                        except:
                            try:
                                price = card.find_element(By.CSS_SELECTOR, "span.price__lower-price").text
                                product['price'] = price.replace('₽', '').replace(' ', '').strip()
                            except:
                                product['price'] = None
                        
                        # Старая цена (если есть скидка)
                        try:
                            old_price = card.find_element(By.CSS_SELECTOR, "del.price__lower-price").text
                            product['old_price'] = old_price.replace('₽', '').replace(' ', '').strip()
                        except:
                            product['old_price'] = None
                        
                        # Ссылка на товар
                        try:
                            link = card.find_element(By.CSS_SELECTOR, "a.product-card__link").get_attribute("href")
                            product['link'] = link.split('?')[0]  # Убираем параметры ссылки
                        except:
                            try:
                                link = card.find_element(By.CSS_SELECTOR, "a.j-card-link").get_attribute("href")
                                product['link'] = link.split('?')[0]
                            except:
                                product['link'] = None
                        
                        # ID товара
                        try:
                            product['id'] = product['link'].split('/')[-2]
                        except:
                            product['id'] = None
                        
                        # Рейтинг и отзывы
                        try:
                            rating_block = card.find_element(By.CSS_SELECTOR, "div.product-card__rating")
                            product['rating'] = rating_block.find_element(By.CSS_SELECTOR, "span.product-card__count").text.strip()
                            product['reviews'] = rating_block.find_element(By.CSS_SELECTOR, "span.product-card__count").text.strip()
                        except:
                            product['rating'] = None
                            product['reviews'] = None
                        
                        if all([product['name'], product['price'], product['link']]):
                            products.append(product)
                            
                    except Exception as e:
                        print(f"Ошибка при парсинге карточки товара: {e}")
                        continue
                
                # Если собрали достаточно товаров, выходим
                if len(products) >= max_products:
                    break
            
            return products[:max_products]
            
        except Exception as e:
            print(f"Ошибка при выполнении поиска: {e}")
            return []
    
    def save_to_json(self, data, filename='wildberries_products.json'):
        """Сохранение данных в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Данные успешно сохранены в файл {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")
    
    def close(self):
        """Закрытие браузера"""
        self.driver.quit()


if __name__ == "__main__":
    parser = WildberriesParser()
    try:
        search_query = input("Введите запрос для поиска на Wildberries: ")
        max_products = int(input("Введите максимальное количество товаров для сбора (по умолчанию 50): ") or 50)
        
        print("Начинаем парсинг... Это может занять несколько минут.")
        products = parser.search_products(search_query, max_products)
        
        if products:
            print(f"Найдено {len(products)} товаров")
            filename = f"wildberries_{search_query.replace(' ', '_').lower()}.json"
            parser.save_to_json(products, filename)
            
            # Выводим пример первых 3 товаров
            print("\nПримеры найденных товаров:")
            for i, product in enumerate(products[:3], 1):
                print(f"{i}. {product.get('brand', 'Бренд не указан')} - {product.get('name', 'Название не указано')}")
                print(f"   Цена: {product.get('price', 'Нет данных')} руб.")
                if product.get('old_price'):
                    print(f"   Старая цена: {product.get('old_price')} руб.")
                print(f"   Ссылка: {product.get('link')}\n")
        else:
            print("Не удалось найти товары по заданному запросу. Возможные причины:")
            print("- Изменилась структура сайта Wildberries")
            print("- Нет товаров по вашему запросу")
            print("- Сработала защита от парсинга")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        parser.close()