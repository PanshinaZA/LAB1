import grpc
from datetime import datetime, timedelta
import calendar_pb2
import calendar_pb2_grpc

class CalendarClient:
    def __init__(self, host='localhost', port=50054):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = calendar_pb2_grpc.CalendarServiceStub(self.channel)
    
    def print_event(self, event):
        """Выводит информацию о событии"""
        print("\n" + "=" * 60)
        print(f"СОБЫТИЕ: {event.title}")
        print("=" * 60)
        print(f"ID: {event.event_id}")
        print(f"Описание: {event.description}")
        print(f"Начало: {event.start_time}")
        print(f"Окончание: {event.end_time}")
        print(f"Место: {event.location}")
        print(f"Организатор: {event.organizer}")
        print(f"Статус: {event.status}")
        print(f"Участники: {', '.join(event.attendees) if event.attendees else 'нет'}")
        print(f"Создано: {event.created_at}")
        print(f"Обновлено: {event.updated_at}")
        print("=" * 60)

    def input_datetime(self, prompt):
        """Ввод даты и времени с валидацией"""
        while True:
            try:
                date_str = input(f"{prompt} (ГГГГ-ММ-ДД ЧЧ:ММ): ").strip()
                if not date_str:
                    return None
                
                # Парсим дату и время
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                return dt.isoformat()
            except ValueError:
                print("Ошибка формата! Используйте: ГГГГ-ММ-ДД ЧЧ:ММ (например: 2024-12-25 14:30)")

    def create_event(self):
        """Создает новое событие"""
        print("\n--- СОЗДАНИЕ НОВОГО СОБЫТИЯ ---")
        
        title = input("Название события: ").strip()
        description = input("Описание: ").strip()
        
        # Ввод времени начала и окончания
        print("\nВведите время начала события:")
        start_time = self.input_datetime("Время начала")
        if not start_time:
            print("Время начала обязательно!")
            return False
        
        print("\nВведите время окончания события:")
        end_time = self.input_datetime("Время окончания")
        if not end_time:
            print("Время окончания обязательно!")
            return False
        
        location = input("Место проведения: ").strip()
        organizer = input("Организатор (email): ").strip()
        
        print("Участники (введите через запятую): ")
        attendees_input = input().strip()
        attendees = [a.strip() for a in attendees_input.split(',')] if attendees_input else []
        
        try:
            response = self.stub.CreateEvent(calendar_pb2.EventDetails(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                attendees=attendees,
                organizer=organizer
            ))
            
            if response.success:
                print("УСПЕХ: Событие успешно создано!")
                self.print_event(response.event)
            else:
                print(f"ОШИБКА: {response.message}")
                
            return response.success
            
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e.details()}")
            return False
    
    def get_event(self):
        """Получает информацию о событии"""
        print("\n--- ПОЛУЧЕНИЕ ИНФОРМАЦИИ О СОБЫТИИ ---")
        event_id = input("Введите ID события: ").strip()
        
        try:
            event = self.stub.GetEvent(calendar_pb2.EventRequest(event_id=event_id))
            
            if event.status == "not_found":
                print(f"Событие с ID '{event_id}' не найдено")
            else:
                self.print_event(event)
                
            return True
            
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e.details()}")
            return False
    
    def update_event(self):
        """Обновляет существующее событие"""
        print("\n--- ОБНОВЛЕНИЕ СОБЫТИЯ ---")
        event_id = input("Введите ID события для обновления: ").strip()
        
        try:
            # Сначала получаем текущие данные события
            current_event = self.stub.GetEvent(calendar_pb2.EventRequest(event_id=event_id))
            
            if not current_event.event_id or current_event.status == "not_found":
                print(f"Событие с ID '{event_id}' не найдено")
                return False
            
            print("Текущие данные события:")
            self.print_event(current_event)
            print("\nВведите новые данные (оставьте пустым чтобы оставить текущее значение):")
            
            # Ввод новых данных
            title = input(f"Название [{current_event.title}]: ").strip()
            description = input(f"Описание [{current_event.description}]: ").strip()
            
            print("\nВремя начала события:")
            start_time = self.input_datetime(f"Время начала [{current_event.start_time}]")
            
            print("\nВремя окончания события:")
            end_time = self.input_datetime(f"Время окончания [{current_event.end_time}]")
            
            location = input(f"Место проведения [{current_event.location}]: ").strip()
            organizer = input(f"Организатор [{current_event.organizer}]: ").strip()
            
            print(f"Текущие участники: {', '.join(current_event.attendees) if current_event.attendees else 'нет'}")
            print("Новые участники (введите через запятую, оставьте пустым чтобы не менять): ")
            attendees_input = input().strip()
            
            # Используем текущие значения если новые не введены
            event_details = calendar_pb2.EventDetails(
                event_id=event_id,
                title=title if title else current_event.title,
                description=description if description else current_event.description,
                start_time=start_time if start_time else current_event.start_time,
                end_time=end_time if end_time else current_event.end_time,
                location=location if location else current_event.location,
                organizer=organizer if organizer else current_event.organizer,
                attendees=list(current_event.attendees)  # по умолчанию текущие участники
            )
            
            # Обновляем участников если введены новые
            if attendees_input:
                event_details.attendees[:] = [a.strip() for a in attendees_input.split(',') if a.strip()]
            
            response = self.stub.UpdateEvent(event_details)
            
            if response.success:
                print("УСПЕХ: Событие успешно обновлено!")
                self.print_event(response.event)
            else:
                print(f"ОШИБКА: {response.message}")
                
            return response.success
            
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e.details()}")
            return False
    
    def list_events(self):
        """Выводит список событий"""
        print("\n--- СПИСОК СОБЫТИЙ ---")
        
        try:
            # Получаем все события
            events = self.stub.ListEvents(calendar_pb2.EventsFilter())
            
            if events.total_count == 0:
                print("Событий не найдено")
                return True
            
            print(f"Найдено событий: {events.total_count}\n")
            
            for i, event in enumerate(events.events, 1):
                start_dt = datetime.fromisoformat(event.start_time)
                print(f"{i}. {event.title}")
                print(f"   Время: {start_dt.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Организатор: {event.organizer}")
                print(f"   Статус: {event.status}")
                print(f"   ID: {event.event_id}")
                print()
            
            return True
            
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e.details()}")
            return False
    
    def delete_event(self):
        """Удаляет событие"""
        print("\n--- УДАЛЕНИЕ СОБЫТИЯ ---")
        event_id = input("Введите ID события для удаления: ").strip()
        
        try:
            response = self.stub.DeleteEvent(calendar_pb2.EventRequest(event_id=event_id))
            
            if response.success:
                print(f"УСПЕХ: {response.message}")
            else:
                print(f"ОШИБКА: {response.message}")
                
            return response.success
            
        except grpc.RpcError as e:
            print(f"Ошибка gRPC: {e.details()}")
            return False

def main():
    """Основная функция клиента"""
    print("=== Calendar Service Client ===")
    print("Доступные команды:")
    print("  create - создать новое событие")
    print("  get    - получить информацию о событии")
    print("  update - обновить событие")
    print("  list   - список всех событий")
    print("  delete - удалить событие")
    print("  exit   - выйти")
    print("=" * 40)
    
    client = CalendarClient()
    
    while True:
        print("\nВведите команду: ", end="")
        command = input().strip().lower()
        
        if command == 'exit':
            print("Выход из программы...")
            break
        
        elif command == 'create':
            client.create_event()
        
        elif command == 'get':
            client.get_event()
        
        elif command == 'update':
            client.update_event()

        elif command == 'list':
            client.list_events()
        
        elif command == 'delete':
            client.delete_event()
        
        else:
            print("Неизвестная команда. Доступные команды: create, get, update, list, delete, exit")

if __name__ == '__main__':
    main()