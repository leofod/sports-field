# Поиск спортинвых площадок

## Вставка ключа API Яндекс Карт
В файле'/fields/templates/showMap.html' для успешного функционирования вставьте ключ.

```
<script src="https://api-maps.yandex.ru/2.1/?apikey=API_KEY&lang=ru_RU" type="text/javascript"></script>
```

## Изменение конфигурационного файла
Отредактируйте файл 'users/mail.ini' для почтовой рассылки. 

```
user = MAIL
passwd = PASSWORD
server = MAIL_SERVER
port = PORT
```
