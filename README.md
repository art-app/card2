# Герменевтика · тренажёр к экзамену

Telegram Mini App — учебный тренажёр к экзаменам: несколько **предметов**, в каждом —
режим **теста** (вопросы пяти типов с проверкой, пояснениями и самооценкой) и/или режим
**Flash-карточек** (термин → определение, повтор по интервалам). Старт — экран выбора предмета.
Интерфейс обёрнут в нативную среду Telegram: навигация на `MainButton`/`BackButton`,
тема и акцент подстраиваются под клиент пользователя (светлая/тёмная).

## Что внутри

```
trainer/
├── webapp/
│   ├── index.html      # Mini App: движок (UI + Telegram WebApp SDK), без данных
│   ├── data/           # контент предметов (подгружается через fetch)
│   │   ├── subjects.json          # манифест: список предметов
│   │   ├── germenevtika.json      # предмет (тест)
│   │   ├── istoriya-germenevtiki.json
│   │   └── istoriya-hristianstva.json  # предмет (флеш-карточки)
│   └── Dockerfile      # nginx со статикой (index.html + data/)
├── bot/
│   ├── bot.py          # бот на aiogram 3.x — открывает Mini App
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── .github/workflows/  # CI (PR) и Deploy (push в main → GHCR → сервер)
├── docker-compose.yml  # webapp за Traefik + бот
├── .env.example        # DOMAIN, TRAEFIK_*, BOT_TOKEN
└── README.md
```

`webapp/index.html` — самодостаточная страница. Ключевые особенности дизайна и интеграции:
- **Нативная обвязка Telegram** — действие шага вынесено на `MainButton`
  (Проверить → Дальше → Завершить → Пройти заново), возврат на `BackButton`;
  своя верхняя/нижняя панель убрана, заголовок отдан хосту Telegram. Есть стартовый экран и экран итогов.
- **Тема под Telegram** — цвета (фон, секции, текст, разделители) берутся из `themeParams`;
  акцент по умолчанию синий `#2481CC` в светлой теме и фиолетовый `#8774E1` в тёмной,
  цвет шапки/фона задаётся под текущую тему; есть реакция на `themeChanged`.
- **Пояснение не прячется** — после ответа пояснение раскрывается сразу под вариантами,
  подсвечивается рамкой акцента, экран автоскроллит к нему, срабатывает `HapticFeedback`.
- шрифт Manrope подключён через Google Fonts; на старте вызывается `ready()`, `expand()`,
  отключаются вертикальные свайпы;
- прогресс хранится **отдельно по каждому предмету** в `localStorage` и зеркалируется в Telegram
  **CloudStorage** (ключи `trainer_quiz_v3_<id>` для теста и `trainer_flash_v3_<id>` для карточек),
  поэтому синхронизируется между устройствами пользователя.

Вне Telegram (обычный браузер) страница работает в резервном режиме: внизу появляется панель,
имитирующая `MainButton`/`BackButton`, тема следует системной (`prefers-color-scheme`),
без облачной синхронизации. Вся логика идентична.

## Типы заданий

| Тип        | Что делает пользователь                                  |
|------------|---------------------------------------------------------|
| `mc`       | выбирает один вариант                                   |
| `match`    | сопоставляет/классифицирует через выпадающие списки      |
| `sequence` | расставляет пункты по порядку нажатиями                  |
| `fill`     | вписывает пропущенные слова                              |
| `open`     | смотрит образец ответа и ставит самооценку «Знал/Повторить» |

Отдельно от теста есть режим **Flash-карточек**: колоды группируются по билетам / темам / «на повтор»,
карточка переворачивается (вопрос → ответ с примером и кнопкой «Озвучить»), оценка «Знал/Повторить»
задаёт интервал следующего показа (простое интервальное повторение по «коробкам»).

## Запуск

### 1. Захостить webapp по HTTPS

Telegram Mini App требует **HTTPS**. Любой статический хостинг подойдёт. Примеры:

**GitHub Pages**
```bash
# содержимое webapp/ положить в ветку gh-pages или папку /docs
# Settings → Pages → выбрать источник
# URL: https://<username>.github.io/<repo>/
```

**Vercel / Netlify** — задеплоить папку `webapp/` как статический сайт.

**Свой сервер** — отдавать `webapp/index.html` за nginx/Caddy с TLS.

Для локальной отладки используйте туннель (`cloudflared tunnel --url http://localhost:8000`
или `ngrok http 8000`) — он даст временный HTTPS-адрес.

### 2. Создать бота

1. У [@BotFather](https://t.me/BotFather) → `/newbot`, получить токен.
2. (Опционально) `/setmenubutton` или `/newapp` — настроить Mini App в BotFather.

### 3. Запустить бота

```bash
cd bot
cp .env.example .env          # вписать BOT_TOKEN и WEBAPP_URL (HTTPS-адрес из шага 1)
pip install -r requirements.txt
python bot.py
```

После запуска у бота работают:
- `/start` — приветствие и кнопка «📖 Открыть тренажёр»;
- `/trainer` — открыть тренажёр;
- синяя кнопка-меню слева от поля ввода (`MenuButtonWebApp`).

## Деплой на свой сервер за Traefik (Docker)

В репозитории есть готовая сборка: `webapp/Dockerfile` (nginx со статикой),
`bot/Dockerfile` (бот) и `docker-compose.yml` с метками Traefik.

### 1. DNS

Заведите поддомен (например `trainer.example.com`) с A-записью на IP сервера.

### 2. Узнать параметры своего Traefik

```bash
docker ps                                   # найти имя контейнера traefik
docker inspect <traefik> -f '{{json .NetworkSettings.Networks}}'   # имя сети
docker inspect <traefik> | grep -iE 'entrypoints|certificatesresolvers'
```

Нужны три значения: имя внешней сети Traefik, имя HTTPS-entrypoint
(обычно `websecure`) и имя certresolver Let's Encrypt.

### 3. Настроить и запустить

```bash
git clone <этот-репозиторий> trainer && cd trainer
cp .env.example .env          # заполнить DOMAIN, TRAEFIK_*, BOT_TOKEN
docker compose up -d --build
```

Traefik сам выпустит TLS-сертификат для `DOMAIN`. Бот при старте получит
`WEBAPP_URL=https://${DOMAIN}/` и будет открывать страницу по этому адресу.

Проверка:
```bash
docker compose ps
docker compose logs -f bot
curl -I https://trainer.example.com   # ожидаем 200 и валидный сертификат
```

### Обновление

```bash
git pull
docker compose up -d --build
```

## Предметы и контент

Движок (`index.html`) не содержит вопросов — он подгружает их из `webapp/data/` через `fetch`
(поэтому страницу нужно открывать по http(s), а не как `file://`; nginx из `Dockerfile` это обеспечивает).

**`data/subjects.json`** — манифест: список предметов на стартовом экране.

```jsonc
{ "subjects": [
  { "id": "germenevtika",      // совпадает с именем файла предмета
    "title": "Герменевтика",
    "subtitle": "основы",
    "file": "germenevtika.json",
    "icon": "spiral",          // ключ иконки: spiral|clock|book|lang|layers|quote|list|cards
    "modes": ["quiz"],         // ["quiz"], ["flashcards"] или оба
    "quizCount": 14,           // для подписи на карточке предмета
    "cardCount": 0,
    "desc": "…" }
] }
```

**`data/<id>.json`** — сам предмет. Тест и карточки опциональны (что есть — то и доступно):

```jsonc
{
  "id": "...", "title": "...", "subtitle": "...", "description": "...",
  "questions": [ /* массив заданий: типы mc | match | sequence | fill | open */ ],
  "flashcards": {
    "tickets": [
      { "number": 1, "title": "Реформация",
        "questions": [
          { "number": 1, "topic": "Причины Реформации",
            "cards": [
              { "id": "t1q1c1", "front": "вопрос/термин", "back": "ответ",
                "example": "необязательный пример (озвучивается)" }
            ] } ] } ]
  }
}
```

Схема `flashcards` совпадает с форматом выгрузки карточек (билеты → вопросы → карточки `front`/`back`),
`id` карточки — стабильный ключ её прогресса.

### Как добавить новый предмет

1. Положить `data/<id>.json` с контентом (тест и/или карточки).
2. Добавить запись о нём в `data/subjects.json` (с `quizCount`/`cardCount` для подписи).
3. Перезалить статику (`docker compose up -d --build`) — стартовый экран подхватит новый предмет.
