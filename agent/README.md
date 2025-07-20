# LISA Linux Agent

## Назначение

Linux-агент LISA имитирует действия пользователя в инфраструктуре, выполняет активности (открытие приложений, работу с файлами, веб-поиск и др.), отправляет heartbeat на backend и поддерживает headless-режим для невидимого запуска GUI-приложений.

---

## Быстрый старт

1. **Сборка или получение бинарника**
   - Используйте предоставленный `main.bin` или соберите самостоятельно (см. Nuitka/pyinstaller).
2. **Настройте конфиг**
   - Отредактируйте `agent_config.json` (пример ниже).
3. **Запуск**
   - Через скрипт: `bash LinuxScript.sh`
   - Или вручную: `./main.bin` (от имени пользователя, указанного в config)

---

## agent_config.json (пример)
```json
{
  "employee_id": 1,
  "name": "test",
  "role": "admin",
  "work_start_time": "09:00:00",
  "work_end_time": "18:00:00",
  "activity_rate": 1.0,
  "actions": [
    {"id": 1, "name": "firefox", "url": "duckduckgo.com", "os": "linux"},
    {"id": 2, "name": "LibreOffice Writer", "os": "linux"},
    {"id": 3, "name": "LibreOffice Calc", "os": "linux"}
  ]
}
```
- `role`: dev/admin/user — влияет на поведение обработчиков
- `activity_rate`: интенсивность действий (0.1–1.0)

---

## Архитектура и обработчики

- **Главный цикл**: `Behaviour.run_loop()`
  - Периодически выбирает действие, вызывает обработчик по роли
  - Отправляет heartbeat на backend (`/agents/{employee_id}/heartbeat`) раз в 2 часа
- **Обработчики**: отдельные функции для Firefox, LibreOffice, GIMP, текстовых редакторов и терминала
  - Все действия headless/hidden (через `--headless` или Xvfb)
  - Файлы создаются в `~/LISA_work_files`
  - Примеры см. в `handlers.py` и `README_ACTIVITIES.md`
- **safe_run**: интерактивные команды (less, man и др.) автоматически закрываются (отправляется 'q')

---

## Heartbeat
- Агент отправляет POST-запрос на backend `/agents/{employee_id}/heartbeat` с `{"status": "ok"}`
- Интервал: 2 часа
- Backend вычисляет online/offline по времени последнего heartbeat

---

## Headless/hidden режим
- Все окна приложений открываются скрыто:
  - LibreOffice: `--headless`
  - Firefox: headless-режим Selenium
  - GIMP, gedit: через Xvfb
- Агент не взаимодействует с реальным рабочим столом пользователя

---

## Лучшие практики для добавления активностей
- Используйте try-except для обработки ошибок
- Логируйте действия через print
- Корректно завершайте процессы (terminate/kill)
- Используйте параметры из action_data
- См. подробности: `agent_linux/README_ACTIVITIES.md`

---

## Развертывание
- Для автоматической установки используйте `deploy.sh` и `LinuxScript.sh`
- Скрипты создают пользователя, копируют бинарник и запускают агент
- Пример:
  ```bash
  bash deploy.sh
  ```

---

## Пример расширения
- Для добавления нового приложения реализуйте обработчик по шаблону (см. `README_ACTIVITIES.md`)
- Добавьте ветку в `execute_activity_action`

---

## Контакты и поддержка
- Вопросы и баги: через GitHub Issues или напрямую разработчику
