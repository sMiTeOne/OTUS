# Запуск
```
python httpd.py
```

Параметры запуска:
- `-a --address [ADDRESS]` - IP-адрес Web-сервера (по умолчанию: `127.0.0.1`)
- `-p --port [PORT]` - порт Web-сервера (по умолчанию: `1337`)
- `-r --root [ROOT]` - путь к директории с документами (по умолчанию: `./`)
- `-i --index [INDEX]` - название файла индекса (по умолчанию: `index.html`)


# Архитектура
В реализации веб-сервера использовалась архитектура prefork


# Запуск тестов
```
pytest test.py
```


# Результаты нагрузочного тестирования
```
ab -n 50000 -c 100 -r http://127.0.0.1:1337/

Benchmarking 127.0.0.1 (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        localhost
Server Hostname:        127.0.0.1
Server Port:            1337

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   114.645 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      7350000 bytes
HTML transferred:       0 bytes
Requests per second:    436.13 [#/sec] (mean)
Time per request:       229.290 [ms] (mean)
Time per request:       2.293 [ms] (mean, across all concurrent requests)
Transfer rate:          62.61 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2  32.7      0     533
Processing:     0  226 326.5     23    2554
Waiting:        0  176 288.9     17    2060
Total:          0  228 328.3     23    2554

Percentage of the requests served within a certain time (ms)
  50%     23
  66%     34
  75%    529
  80%    533
  90%    544
  95%   1039
  98%   1054
  99%   1066
 100%   2554 (longest request)
```
