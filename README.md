# Герменевтика · тренажёр к экзамену

Telegram Mini App — тренажёр на флеш-карточках для подготовки к экзамену по герменевтике.
20 вопросов пяти типов с проверкой, пояснениями, прогрессом и самооценкой.

## Что внутри

```
trainer/
├── webapp/
│   ├── index.html      # Mini App: дизайн + Telegram WebApp SDK
│   └── Dockerfile      # nginx со статикой
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

`webapp/index.html` — самодостаточная страница. Отличия от исходного дизайна:
- шрифт Manrope подключён через Google Fonts (вместо встроенных blob-шрифтов бандла);
- подключён `telegram-web-app.js`: на старте вызывается `ready()`, `expand()`,
  отключаются вертикальные свайпы, задаётся цвет шапки/фона;
- вибро-отклик использует Telegram `HapticFeedback`;
- прогресс хранится в `localStorage` **и** зеркалируется в Telegram **CloudStorage**,
  поэтому он синхронизируется между устройствами пользователя.

Вне Telegram (обычный браузер) страница работает как раньше — просто без облачной синхронизации.

## Типы заданий

| Тип        | Что делает пользователь                                  |
|------------|---------------------------------------------------------|
| `mc`       | выбирает один вариант                                   |
| `match`    | сопоставляет/классифицирует через выпадающие списки      |
| `sequence` | расставляет пункты по порядку нажатиями                  |
| `fill`     | вписывает пропущенные слова                              |
| `open`     | смотрит образец ответа и ставит самооценку «Знал/Повторить» |

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

## Обновление вопросов

Все 20 вопросов лежат в массиве `QUESTIONS` внутри `webapp/index.html`.
Чтобы изменить контент — правьте этот массив; перезагрузка хостинга подхватит изменения.
