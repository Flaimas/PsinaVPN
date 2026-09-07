# 🐕 PsinaVPN — Backend & Telegram Bot

Асинхронный сервис управления VPN-инфраструктурой на базе **Xray-core** и панели **Remnawave**. Проект построен на современном стекe Python + FastAPI + Aiogram 3 с полной контейнеризацией через Docker.

---

## 🛠 Технологический стек

* **Language:** Python 3.14
* **Package Manager:** [uv](https://github.com/astral-sh/uv)
* **Frameworks:** Aiogram 3, FastAPI, Pydantic v2
* **Database & ORM:** PostgreSQL 15, SQLAlchemy 2.0 (Async), Alembic
* **Cache & Broker:** Redis 7
* **Payments:** YooKassa API
* **Deployment:** Docker, Docker Compose, GitHub Actions (CI/CD)

---

## 🚀 Быстрый старт на VPS (Production)

### Требования
1) Телеграм бот работает на основе панели [Remnawave](https://github.com/remnawave)
2) Для работы приложения на сервере требуется **Docker**. Если он ещё не установлен, выполните команду:

```bash
curl -fsSL [https://get.docker.com](https://get.docker.com) | sh
```

---

### Пошаговая установка

1. **Создайте директорию проекта и перейдите в неё:**
   ```bash
   mkdir -p /opt/psina-bot && cd /opt/psina-bot
   ```

2. **Загрузите конфигурационные файлы из репозитория:**
   ```bash
   curl -o docker-compose.yml [https://raw.githubusercontent.com/Flaimas/PsinaVPN/main/docker-compose.yml](https://raw.githubusercontent.com/Flaimas/PsinaVPN/main/docker-compose.yml)
   curl -o .env [https://raw.githubusercontent.com/Flaimas/PsinaVPN/main/.env.example](https://raw.githubusercontent.com/Flaimas/PsinaVPN/main/.env.example)
   ```

3. **Настройте переменные окружения:**
   ```bash
   nano .env
   ```
   *Укажите токен бота (`BOT_TOKEN`), параметры подключения к БД, секреты Redis и ключи внешних API.*

4. **Запустите контейнеры и проверьте логи:**
   ```bash
   docker compose up -d && docker compose logs -f -t
