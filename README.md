# Сравниваем вакансии программистов 

Сервис для сбора статистики по заработной плате программистов среди наиболее популярных языков программирования на основе данных HeadHunter и SuperJob.

### Как установить

 - Для использования скрипта необходимо зарегистрироваться на сайте [SuperJob](https://api.superjob.ru/)
   и получить токен.
 - Полученный токен присвоить переменной окружения в файле ".env":
```python
   SUPERJOB_TOKEN=ВашТокен
```
 - Python3 должен быть уже установлен.
 - Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```python
   pip install -r requirements.txt
   ```
 - Для запуска скрипта используйте команду:
```python
   python main.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
