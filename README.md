Структура папок:

```
component
  reader
  infer
  visitors_counter
  alerter
  ui_frontend
  ui_backend
lib
  mqtt_bus
  mysql_driver
  hnsw_driver
  ...
```


В каждой папке:
```
__init__.py
requirements.txt
...
```


Работа с логгером:

```
import logging


log = logging.getLogger()
...
```

Деплой фронтенда:
```
bash /opt/projects/componrnt/http_api/deploy/make.sh
```