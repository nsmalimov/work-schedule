Изначально думал реализовать внутри django-проекта, используя его механизм миграци и фикстур для инициализации
базы данных, но решил использовать asyncio, чтобы в будущем можно было использовать в асинхронном сервере (как например aiohttp или sanic). Вообще 
по ощущениям писать асинхронный код проще.

### docker
Для интеграционных тестов можно поднять локальную базу PSQL через docker-образ.

`docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=123 postgres`

`docker ps --all`

Затем необходимо создать базу данных "timetable" (см. settings.py).

`CREATE DATABASE timetable`

### Структура базы данных

см. SQL - скрипт с миграцией
 ./timetable/init.sql
 
### Условия задачи
1. Менеджеры должны видеть какие слоты доступны на указанный день с учётом всех расписаний, взятых и не взятых задач.
2. Как бы установщики не брали задачи не должно оставаться задач, которую не сможет взять никто (допускаем, что расписание менять нельзя).

Старт дня с 03:00:00 до 02:59:59.

Максимальная продолжительность задачи: от 30 минут до 4 часов.

### Заполнение таблиц тестовыми данными

При создании тестовых данных, за основу взял реальные данные со скриншотов с расписанием.

Учитывал, что данные нужны в различных вариациях:

Тестовые кейсы:

Для работников:
* Есть работники, которые сегодня не работают. 
* Есть свободные полностью работники.
* Есть работники, которые полностью загружены задачами.

Для задач:
* Есть взятые задачи. 
* Есть свободные задачи, которые пока никто не взял.
* Есть задачи на 30 минут.

Общие:
* Нет смысла рассматривать такой кейс, когда у нас нет свободных слотов. Так как формально
он будет покрыт и в случае, когда есть слоты.
* Нужен кейс, где будет проверен вариант, когда 2 таска могут быть взяты 2-мя работникамив разных ситуациях,
не всегда оптимальных.

2 таска 
с 10 до 12 и с 12 до 16.



Скрипт для генерации данных и вставки их в бд:
`python ./timetable/tests/data_generator.py free_exist`

### Алгоритм

1. Сделать запросы 
2. Максимально возможный интервал
3. Берём за условие, что в системе все данные валидны. Иными словами не может быть такого, что
существующие таски не распределяются по всем работникам без "лишнего" времени.
4. Либо заморачиваться с новой сущностью "интервал", и во время взятия кем-либо нового
 таска апдейтить и эту сущность, что кажется сложнее, чем через join взять воркера и таски его и посчитать на лету кодом.

    Выбрал второй вариант.

5. Существенным упрощением является то, что нам не нужно знать количество свободных интервалов на определенную продолжительность
и время. Так как пересчёты будут происходить после создания таска для каждого менеджера.
Соответственно нам нужно лишь прежложить доступные варианты слотов без указания их точного количества.

    Это позволяет написать алгоритм, в котором мы сначало узнаём все доступные слоты с учётом фильтра по времени работы воркеров и взятых ими тасков, а потом на основе данных о невзятых тасках

6. Учитываем, что невозможен кейс, когда у нас слот по 4h и 4 слота по 1h, и 1 работник, так как в этом
случае это не валидное условие данных, сюда же все производные такого случая.

### Тесты

Я не стал писать тесты на запросы в базу и на вставку.
 
Сам алгоритм протестировал интеграционно (через реальное хождение в базу) без моков запросов в базу, что достаточно
трудоёмко.

Показалось более разумным тестировать сам алгоритм, поэтому тест получился через хождение в базу, когда мы в базу вставляем данные, а
на выходе проверяем правильность работы функций.

Запускать тесты: `pytest`

Тестировал через pytest: 
https://docs.pytest.org/en/latest/getting-started.html

Либа с декораторами для асинхронных вызовов функций:
https://github.com/pytest-dev/pytest-asyncio

#### Что можно улучшить?
1. Слишком много циклов, код не оптимальный, нужно оптимизировать.
2. Написать качественные инапп тесты, без реального хождения в базу, через моки запросов. 
Написать все кейсы, чтобы проверить полностью логику, включая граничные случаи. 
3. Переделать класс PSQLWorker, создать отдельный класс с дата-логикой, а его оставить только для
хождения в базу.

#### Алгоритм

Краткое описание работы алгоритма. Для более подробного пониманиия лучше смотреть в код. 

1. Взять через join всех работников в тасками при условиие, что работник сегодня работает и не загружен на полную. 
2. По каждому работнику и его времени, разрезать его время на мини-временные отрезки, максимальной продолжительностью по
4 часа. Другими словами, если работник работает с 10 до 16. 

   То временные отрезки будут:
   * с 10 до 11
   * с 10 до 12
   * с 10 до 13
   * с 10 до 14
   * ...   
   
   с шагом 1 час. Всего таких отрезков: 17

   Затем из этих получившихся промежутков мы вырезаем те, которые уже заняты таском, который взял работник. То есть,
   если у работника есть взятый таск длительностью 3 часа и который длиться с 10 до 13, следовательно, мы 
   должны убрать доступные промежутки времени, которые входят во время этого таска, такие как:
   * с 10 до 11
   * с 10 до 12
   * с 10 до 13
   * c 10 до 14
   * c 11 до 12
   * c 11 до 13
   * c 11 до 14
   * ...
   
3. Получить свободные таски, с условием, что он никем не взят.

4. 