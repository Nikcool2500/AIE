# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

или

```bash
uv run eda-cli overview data/S02-hw-dataset.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`);
- `--max_hist_columns` - максимум числовых колонок для гистограмм (по умолчанию `6`);
- `--top_k_categories` - топ k категориальных признаков (по умолчанию `5`);
- `--title` - заголовок отчёта (по умолчанию `EDA-отчёт`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports --max-hist-columns 10 --top-k-categories 8 --title "Новый анализ данных"
```

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown c заголовком "Новый анализ данных";
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-8 категорий по строковым признакам;
- `hist_*.png` – гистограммы из максимум 10 числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

### Случайный пример выборки

```bash
uv run eda-cli sample data/example.csv --n 10 --sep "," --encoding "utf-8"
```

Параметры:

- `--path` – путь к CSV-файлу;
- `--n` – количество строк для вывода (по умолчанию `10`);
- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`);

## Тесты

```bash
uv run pytest -q
```

# S04 – eda_cli: HTTP-сервис качества датасетов (FastAPI)

Расширенная версия проекта `eda-cli` из Семинара 03.

К существующему CLI-приложению для EDA добавлен **HTTP-сервис на FastAPI** с эндпоинтами `/health`, `/quality` и `/quality-from-csv`.  
Используется в рамках Семинара 04 курса «Инженерия ИИ».

---

## Связь с S03

Проект в S04 основан на том же пакете `eda_cli`, что и в S03:

- сохраняется структура `src/eda_cli/` и CLI-команда `eda-cli`;
- добавлен модуль `api.py` с FastAPI-приложением;
- в зависимости добавлены `fastapi` и `uvicorn[standard]`.

Цель S04 – показать, как поверх уже написанного EDA-ядра поднять простой HTTP-сервис.

---

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему
- Браузер (для Swagger UI `/docs`) или любой HTTP-клиент:
  - `curl` / HTTP-клиент в IDE / Postman / Hoppscotch и т.п.

---

## Инициализация проекта

В корне проекта (каталог S04/eda-cli):

```bash
uv sync
```

Команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml` (включая FastAPI и Uvicorn);
- установит сам проект `eda-cli` в окружение.

---

## Запуск CLI (как в S03)

CLI остаётся доступным и в S04.

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` - разделитель (по умолчанию `,`);
- `--encoding` - кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

В результате в каталоге `reports/` появятся:

- `report.md` - основной отчёт в Markdown;
- `summary.csv` - таблица по колонкам;
- `missing.csv` - пропуски по колонкам;
- `correlation.csv` - корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` - top-k категорий по строковым признакам;
- `hist_*.png` - гистограммы числовых колонок;
- `missing_matrix.png` - визуализация пропусков;
- `correlation_heatmap.png` - тепловая карта корреляций.

---

## Запуск HTTP-сервиса

HTTP-сервис реализован в модуле `eda_cli.api` на FastAPI.

### Запуск Uvicorn

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Пояснения:

- `eda_cli.api:app` - путь до объекта FastAPI `app` в модуле `eda_cli.api`;
- `--reload` - автоматический перезапуск сервера при изменении кода (удобно для разработки);
- `--port 8000` - порт сервиса (можно поменять при необходимости).

После запуска сервис будет доступен по адресу:

```text
http://127.0.0.1:8000
```

---

## Эндпоинты сервиса

### 1. `GET /health`

Простейший health-check.

**Запрос:**

```http
GET /health
```

**Ожидаемый ответ `200 OK` (JSON):**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

Пример проверки через `curl`:

```bash
curl http://127.0.0.1:8000/health
```

---

### 2. Swagger UI: `GET /docs`

Интерфейс документации и тестирования API:

```text
http://127.0.0.1:8000/docs
```

Через `/docs` можно:

- вызывать `GET /health`;
- вызывать `POST /quality` (форма для JSON);
- вызывать `POST /quality-from-csv` (форма для загрузки файла).
- вызывать `POST /quality-flags-from-csv` (форма для загрузки файла).

---

### 3. `POST /quality` – заглушка по агрегированным признакам

Эндпоинт принимает **агрегированные признаки датасета** (размеры, доля пропусков и т.п.) и возвращает эвристическую оценку качества.

**Пример запроса:**

```http
POST /quality
Content-Type: application/json
```

Тело:

```json
{
  "n_rows": 10000,
  "n_cols": 12,
  "max_missing_share": 0.15,
  "numeric_cols": 8,
  "categorical_cols": 4
}
```

**Пример ответа `200 OK`:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.8,
  "message": "Данных достаточно, модель можно обучать (по текущим эвристикам).",
  "latency_ms": 3.2,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false
  },
  "dataset_shape": {
    "n_rows": 10000,
    "n_cols": 12
  }
}
```

**Пример вызова через `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{"n_rows": 10000, "n_cols": 12, "max_missing_share": 0.15, "numeric_cols": 8, "categorical_cols": 4}'
```

---

### 4. `POST /quality-from-csv` – оценка качества по CSV-файлу

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает оценку качества датасета в том же формате, что `/quality`.

**Запрос:**

```http
POST /quality-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `ok_for_model` - результат по эвристикам;
- `quality_score` - интегральный скор качества;
- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

---

### 5. `POST /quality-flags-from-csv` – флаги качества по CSV-файлу
### 5. `POST /quality-flags-from-csv` – флаги качества по CSV-файлу

Эндпоинт принимает CSV-файл и **возвращает только флаги качества** датасета — без скоринга, без сообщений, без ok_for_model.
Используется для получения «сырого» набора эвристик (включая новые из HW03).

Внутри эндпоинта:

* CSV читается в `pandas.DataFrame`;
* вызываются функции из `eda_cli.core`:

  * `summarize_dataset`,
  * `missing_table`,
  * `compute_quality_flags` *(без передачи `df`)*;
* а также **дополнительные эвристики вызываются явно**:

  * `has_high_cardinality_categoricals(summary)`,
  * `has_suspicious_id_duplicates(summary, df)`;
* итоговый ответ содержит только:

```json
{
  "flags": {
    "...": ...
  }
}
```

#### Пример запроса

```http
POST /quality-flags-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger UI (`/docs`):

1. открыть `POST /quality-flags-from-csv`,
2. нажать **Try it out**,
3. выбрать CSV-файл,
4. нажать **Execute**.

#### Пример запроса через `curl`

```bash
curl -X POST "http://127.0.0.1:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

#### Пример ответа `200 OK`

```json
{
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": true,
    "has_constant_columns": false,
    "has_high_cardinality_categoricals": true,
    "has_suspicious_id_duplicates": false,
    "has_many_zero_values": true
  }
}
```

Состав флагов зависит от реализованных эвристик в модуле `core.py` (включая все новые признаки из HW03).

## Структура проекта (упрощённо)

```text
S04/
  eda-cli/
    pyproject.toml
    README.md                # этот файл
    src/
      eda_cli/
        __init__.py
        core.py              # EDA-логика, эвристики качества
        viz.py               # визуализации
        cli.py               # CLI (overview/report)
        api.py               # HTTP-сервис (FastAPI)
    tests/
      test_core.py           # тесты ядра
    data/
      example.csv            # учебный CSV для экспериментов
```

---

## Тесты

Запуск тестов (как и в S03):

```bash
uv run pytest -q
```

Рекомендуется перед любыми изменениями в логике качества данных и API:

1. Запустить тесты `pytest`;
2. Проверить работу CLI (`uv run eda-cli ...`);
3. Проверить работу HTTP-сервиса (`uv run uvicorn ...`, затем `/health` и `/quality`/`/quality-from-csv` через `/docs` или HTTP-клиент).