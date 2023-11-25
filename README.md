# HdRezka API

Исходный код https://github.com/vovaklh/HdRezkaApi

## Запуск

### Параметры запуска python
| Параметр  | Пример | По умолчанию | Описание |
| ------------- | ------------- | ------ | -------- |
| -port  | "8000"  | "8000" | Порт на котором будет запущен сервер |
| -mirrorUrl  | "https://hdrezka.ag"  | "https://hdrezka.ag" | Адрес зеркала hdrezka |
| -ip  | "192.168.1.15"  | "0.0.0.0" | Адрес на котором будет запущен сервер |

### Запуск
```
python3 api.py
```

### Обновление

```
git pull
python3 api.py
```

## Запуск в Docker
### Переменные окружения
| Параметр  | Пример | По умолчанию | Описание |
| ------------- | ------------- | ------ | -------- |
| PORT  | "8000"  | "8000" | Порт на котором будет запущен сервер |
| MIRROR_URL  | "https://hdrezka.ag"  | "https://hdrezka.ag" | Адрес зеркала hdrezka |
| IP  | "192.168.1.15"  | "0.0.0.0" | Адрес на котором будет запущен сервер |


### Пометка
При запуске контейнера, если не указаны переменные окружения, то будут использоваться значения по умолчанию.
Чтобы изменить значения по умолчанию, Требуется по шаблону написать команду для запуска контейнера.
```
docker run -d --name hdrezka_api --restart=always -p 8000:8000 --env MIRROR_URL="https://hdrezka.ag" hdrezka_api
```

### Запуск

```
// Сборка образа
docker build -t hdrezka_api .
// Запуск контейнера
docker run -d --name hdrezka_api --restart=always -p 8000:8000 hdrezka_api
```

### Обновление контейнера

Ручная сборка образа:

```
docker stop hdrezka_api
docker rm hdrezka_api
git pull
docker build -t hdrezka_api .
docker run -d --name hdrezka_api --restart=always -p 8000:8000 hdrezka_api
```

или
    
```
docker stop hdrezka_api
docker rm hdrezka_api
docker pull divarion/hdrezka_api:master
docker run -d --name hdrezka_api --restart=always -p 8000:8000 divarion/hdrezka_api:master
```


## Документация
http://127.0.1.1:8000/api/docs
