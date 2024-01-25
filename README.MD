# Design Guide Bot
Этот телеграм-бот создан по заказу графического дизайнера для привлечения потенциальных клиентов из социальных сетей.

## Клонировать репозиторий
```
$ git clone git@github.com:amedice-dev/desing_guide_bot.git
```

## Зависимости
1. run [docker](https://www.docker.com)
2. создать в корневой папке `.env` файл по примеру `.env.example`

## Запуск приложения 
```shell
docker compose up -d --build
```

## Остановка приложения
```shell
docker compose down
```