# Лабораторная работа №1. Реализация RPC-сервиса с использованием gRPC. Вариант 17
## Цели:
1. Освоить принципы удаленного вызова процедур (RPC) и их применение в распределенных системах;
2. Изучить основы фреймворка gRPC и языка определения интерфейсов Protocol Buffers (Protobuf);
3. Научиться определять сервисы и сообщения с помощью Protobuf;
4. Реализовать клиент-серверное приложение на языке Python с использованием gRPC;
5. Получить практические навыки в генерации кода, реализации серверной логики и клиентских вызовов для различных типов RPC.
## Описание предметной области
Разработать сервис календаря Calendar:

Метод(Unary RPC) CreateEvent(EventDetails) - создаёт новое событие в календаре.
## Архитектура
В основе лабораторной работы лежит классическая клиент-серверная архитектура (Client-Server
Architecture), реализованная с помощью парадигмы удаленного вызова процедур (Remote Procedure Call - RPC).
### 1. Компоненты
#### Сервер (Server). 
Это независимое приложение (server.py), которое выполняет основную "бизнес-логику".
Возможности:

• Предоставляет сервис. Он реализует и "выставляет наружу" сервис Calendar, определенный в контракте.

• Обрабатывает запросы. Он слушает входящие сетевые соединения на определенном порту (50051) и обрабатывает
вызовы от клиентов.

• Выполняет логику. Генерирует введенные данные о дате и событиях, имитируя реальную работу.

• Асинхронность. Использует пул потоков для одновременной обработки нескольких
клиентских запросов.

#### Клиент (Client). 
Это приложение (client.py), которое потребляет функциональность, предоставляемую сервером.
Возможности:

• Инициирует соединение. Устанавливает соединение с сервером по известному адресу (localhost:50051).

• Вызывает удаленные методы. Обращается к методам сервера (CreateEvent) так, как будто
это локальные функции.

• Обрабатывает ответы. Получает и выводит на экран данные, возвращенные сервером

### 2. Взаимодействие и контракт

<img width="591" height="628" alt="image" src="https://github.com/user-attachments/assets/7a64e299-4240-4a2d-bdd1-e3792d51b612" />

Ключевым элементом архитектуры является сервисный контракт (Service Contract), определенный в файле calendar.proto. Роль контракта: этот файл является "единым источником правды" для API. Он строго описывает:

• Какие сервисы доступны (CalendarService).

• Какие методы можно вызвать у каждого сервиса (CreateEvent, GetEvent, UpdateEvent, DeleteEvent, ListEvents).

• Какие данные (сообщения) эти методы принимают (EventRequest) и возвращают (EventResponse).

## Технологический стек
1. Язык определения интерфейсов (IDL): Protocol Buffers (Protobuf)
2. Фреймворк RPC: gRPC
3. Транспортный протокол: HTTP/2
4. Язык программирования: Python 3
5. Ключевые библиотеки Python: a) grpcio b) grpcio-tools
6. Среда выполнения и изоляция: a) ОС: Ubuntu 20.04 (Linux). b) Виртуальное окружение (venv). Инструмент для изоляции зависимостей проекта, гарантирующий, что установленные пакеты (grpcio и др.) не будут конфликтовать с системными или другими проектами.

## Шаг 1. Подготовка окружения
Обновим все пакеты и установим Python. Создаем папку LAB1, в которой подготовим наше виртуальное окружение. Активируем его, а также установим библиотеки gRPC:

<img width="663" height="19" alt="image" src="https://github.com/user-attachments/assets/09838fcd-a207-4fb0-bab5-6334f82310d0" />

<img width="1118" height="184" alt="image" src="https://github.com/user-attachments/assets/630c2fa0-4925-4990-a23c-154fe19f1cd9" />

<img width="662" height="48" alt="image" src="https://github.com/user-attachments/assets/1d93ee83-c2ce-46e4-b550-9110ef6fb3cc" />

<img width="1044" height="155" alt="image" src="https://github.com/user-attachments/assets/3d81b9e4-cd45-47fc-aa0a-1d3f1a837292" />

## Шаг 2. Определение сервиса в .proto файле

```
// Указываем синтаксис proto3
syntax = "proto3";
 // Определяем пакет для нашего сервиса
package calendar;
 // Сервис для занесения новых событий в календарь
service CalendarService {
  // RPC метод для создания нового события
  rpc CreateEvent(EventDetails) returns (EventResponse);
  // RPC метод для получения информации о событии по его ID
  rpc GetEvent(EventRequest) returns (EventDetails);
  // RPC метод для обновления существующего события
  rpc UpdateEvent(EventDetails) returns (EventResponse);
  // RPC метод для удаления события по его ID
  rpc DeleteEvent(EventRequest) returns (EventResponse);
  // RPC метод для получения списка событий с фильтрацией
  rpc ListEvents(EventsFilter) returns (EventList);
}
// Сообщение с детальной информацией о событии
message EventDetails {
  string event_id = 1;
  string title = 2;
  string description = 3;
  string start_time = 4;
  string end_time = 5;
  string location = 6;
  repeated string attendees = 7;
  string organizer = 8;
  string status = 9; // scheduled, cancelled, completed
  string created_at = 10;
  string updated_at = 11;
}
// Сообщение для запроса события по ID
message EventRequest {
  string event_id = 1;
}
// Сообщение-ответ с результатом операции
message EventResponse {
  bool success = 1;
  string message = 2;
  EventDetails event = 3;
}
// Сообщение для фильтрации событий при запросе списка
message EventsFilter {
  string start_date = 1;
  string end_date = 2;
  string organizer = 3;
  string status = 4;
}
// Сообщение со списком событий
message EventList {
  repeated EventDetails events = 1;
  int32 total_count = 2;
}
```
## Шаг 3. Генерация кода
Выполним в терминале команду для генерации Python-классов из .proto файла: 

<img width="1179" height="15" alt="image" src="https://github.com/user-attachments/assets/f3f9b5ab-0b34-4e39-9088-094491d4752d" />

В папке появятся два новых файла: calendar_pb2.py и calendar_pb2_grpc.py, которые содержат сгенерированные классы для клиента и сервера.

<img width="289" height="204" alt="image" src="https://github.com/user-attachments/assets/447daa18-099d-487e-ba13-a1bde346ce46" />

## Шаг 4. Реализация сервера
Создаем файл [server.py](https://github.com/PanshinaZA/LAB1/blob/main/server.py) и прописываем в нем код сервера, аналогично с файлом клиента [client.py](https://github.com/PanshinaZA/LAB1/blob/main/client.py):

<img width="849" height="505" alt="image" src="https://github.com/user-attachments/assets/330f7266-c5d0-4ac1-8d97-79fb661e25f7" />
<img width="810" height="683" alt="image" src="https://github.com/user-attachments/assets/7040f6b3-907a-4769-8075-524b27faefa5" />

## Шаг 5. Запуск и проверка
Откроем новый терминал, активируем виртуальное окружение и запсутим наш сервер:

<img width="665" height="196" alt="image" src="https://github.com/user-attachments/assets/827dd25b-5e2c-4e12-ae8b-5cf1ad84216d" />

Затем откроем второй терминал, в котором запустим клиент:
<img width="682" height="189" alt="image" src="https://github.com/user-attachments/assets/a22ce309-985a-4b94-8466-3760190bfd9e" />

Проверим, все ли команды работают:
<img width="1529" height="370" alt="image" src="https://github.com/user-attachments/assets/2f0dc5c0-c515-470b-8b55-e4442840d7d9" />

## Выводы
В ходе выполнения лабораторной работы освоены принципы удаленного вызова процедур и их применение в распределенных системах, изучены основы фреймворка gRPC и языка определения интерфейсов Protocol Buffers, а также реализовано клиент-серверное приложение на языке Python с использованием gRPC.
