# Лабораторная работа 2. Потоки. Процессы. Асинхронность

**Выполнил:** Шафиков Максим, группа k3339  
**Дата:** 7 мая 2026  
**Ветка:** [`lab2`](https://github.com/MrAmfix/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab2/students/k3339/Shafikov_Maxim/Lr2)

---

## Цель работы

Понять отличия между потоками (threading), процессами (multiprocessing) и асинхронностью (asyncio) в Python, научиться применять каждый подход для параллельного выполнения задач — как вычислительных (CPU-bound), так и ввода-вывода (I/O-bound).

---

## Структура проекта

```
Lr2/
├── README.md                  # этот файл
├── requirements.txt           # зависимости
├── .env-example               # пример переменных окружения
├── docker-compose.yml         # PostgreSQL на конфигурируемом порту из .env
├── config.py                  # общий конфиг (POSTGRES_* → DATABASE_URL)
├── database.py                # асинхронное подключение к БД (SQLAlchemy async)
├── models.py                  # модель ParsedPage
├── task1/
│   ├── threading_sum.py       # Задача 1 — threading
│   ├── multiprocessing_sum.py # Задача 1 — multiprocessing
│   └── async_sum.py           # Задача 1 — asyncio (to_thread)
└── task2/
    ├── threading_parser.py    # Задача 2 — threading + requests + psycopg2
    ├── multiprocessing_parser.py  # Задача 2 — multiprocessing + requests + psycopg2
    └── async_parser.py        # Задача 2 — asyncio + aiohttp + asyncpg
```

---

## Задача 1. Сумма чисел: threading vs multiprocessing vs async

### Описание

Три программы, вычисляющие сумму всех целых чисел от 1 до 1 000 000 000 (один миллиард). Каждая разбивает диапазон на 8 подзадач и выполняет их параллельно:

| Подход | Механизм параллелизма | Модуль |
|--------|----------------------|--------|
| **threading** | Потоки внутри одного процесса | `threading.Thread` |
| **multiprocessing** | Отдельные процессы (обход GIL) | `multiprocessing.Pool` |
| **async** | Асинхронные корутины + `to_thread` для CPU-работы | `asyncio.to_thread` |

Физическая CPU-работа (суммирование) не может быть распараллелена через чистый asyncio, поэтому `asyncio.to_thread` делегирует вычисления в потоки, обеспечивая асинхронное ожидание результатов.

### Результаты замеров

| Подход | Время выполнения |
|--------|-----------------|
| threading | ~X.X с |
| multiprocessing | ~X.X с |
| async (to_thread) | ~X.X с |

### Выводы

- **threading:** потоки разделяют память процесса, но из-за GIL только один поток исполняет Python-код в каждый момент времени. Для CPU-bound задач (вычисления) threading даёт минимальный выигрыш или даже замедление из-за накладных расходов на переключение контекста.
- **multiprocessing:** каждый процесс имеет собственный GIL и полностью независим. CPU-bound задача масштабируется почти линейно с числом ядер. Основной минус — накладные расходы на создание процессов и межпроцессное взаимодействие (сериализация/десериализация данных через pickle).
- **async (to_thread):** по производительности близок к threading (так как под капотом используются те же потоки). Главное преимущество — код остаётся в async/await стиле, что удобно при интеграции в асинхронные приложения (например, FastAPI).

---

## Задача 2. Параллельный парсинг веб-страниц с сохранением в БД

### Описание

Три программы, выполняющие параллельный парсинг 10 веб-страниц, извлечение заголовков (`<title>`) и сохранение результатов в PostgreSQL (таблица `parsed_page`):

| Подход | HTTP-клиент | Драйвер БД | Параллелизм |
|--------|------------|-----------|-------------|
| **threading** | `requests` (синхронный) | `psycopg2` (синхронный) | `ThreadPoolExecutor` |
| **multiprocessing** | `requests` (синхронный) | `psycopg2` (синхронный) | `multiprocessing.Pool` |
| **async** | `aiohttp` (асинхронный) | `asyncpg` через SQLAlchemy async | `asyncio.gather` + `Semaphore` |

### Список URL для парсинга

1. https://www.python.org
2. https://en.wikipedia.org/wiki/Python_(programming_language)
3. https://fastapi.tiangolo.com
4. https://www.sqlalchemy.org
5. https://www.djangoproject.com
6. https://github.com
7. https://en.wikipedia.org/wiki/Web_scraping
8. https://httpbin.org
9. https://pypi.org
10. https://docs.python.org/3/

### Таблица parsed_page

Используется **та же база данных**, что и в лабораторной работе 1 (`finance_db`):

- `id` — первичный ключ (SERIAL)
- `url` — URL спаршенной страницы (TEXT)
- `title` — заголовок страницы (VARCHAR 500)
- `parsed_at` — временная метка парсинга (TIMESTAMPTZ, UTC)

### Результаты замеров

| Подход | Время выполнения |
|--------|-----------------|
| threading | ~X.X с |
| multiprocessing | ~X.X с |
| async | ~X.X с |

### Выводы

- **threading:** хорошо подходит для I/O-bound задач (HTTP-запросы, работа с БД), так как GIL освобождается во время ожидания сети/диска. ThreadPoolExecutor прост в использовании, потоки легковесны.
- **multiprocessing:** избыточен для I/O-bound задач. Накладные расходы на создание процессов и сериализацию превышают потенциальный выигрыш. Каждый процесс открывает собственное подключение к БД, что увеличивает нагрузку на PostgreSQL.
- **async:** наилучший выбор для I/O-bound задач. Позволяет обслуживать сотни соединений в одном потоке, не тратя ресурсы на переключение контекста. Библиотеки `aiohttp` и `asyncpg` предоставляют нативные асинхронные интерфейсы. Единственный минус — необходимость использовать асинхронные версии библиотек.

---

## Общие выводы по лабораторной работе

1. **CPU-bound задачи** (вычисления, обработка данных) → **multiprocessing** — единственный способ получить реальный параллелизм в Python благодаря обходу GIL.
2. **I/O-bound задачи** (сеть, диск, БД) → **asyncio** — наиболее эффективен, так как не тратит память на потоки и минимизирует накладные расходы на переключение контекста.
3. **threading** — компромиссный вариант для I/O-bound, когда нет асинхронных альтернатив библиотек. Проще в использовании, но менее масштабируем, чем asyncio.

### Таблица сравнения подходов

| Критерий | threading | multiprocessing | asyncio |
|----------|-----------|----------------|---------|
| GIL | Да (ограничивает CPU-работу) | Нет (свой GIL на процесс) | Да (один поток) |
| Память | Общая | Изолированная (копия) | Общая |
| Создание | Быстрое | Медленное | Быстрое |
| I/O-bound | Хорошо | Избыточно | Отлично |
| CPU-bound | Плохо | Отлично | Плохо (нужен to_thread) |
| Сложность кода | Низкая | Средняя | Средняя |

---

## Запуск

```bash
# 1. Скопировать .env-example → .env (порт настраивается в POSTGRES_PORT)
cp .env-example .env

# 2. Поднять PostgreSQL (порт берётся из .env)
docker-compose up -d

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить задачу 1
python task1/threading_sum.py
python task1/multiprocessing_sum.py
python task1/async_sum.py

# 5. Запустить задачу 2
python task2/threading_parser.py
python task2/multiprocessing_parser.py
python task2/async_parser.py

# 6. Остановить PostgreSQL
docker-compose down
```
