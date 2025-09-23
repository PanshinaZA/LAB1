import grpc
from concurrent import futures
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import calendar_pb2
import calendar_pb2_grpc

class CalendarServicer(calendar_pb2_grpc.CalendarServiceServicer):
    def __init__(self):
        self.events_db = {}
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Инициализирует тестовые данные"""
        now = datetime.now()
        
        sample_events = [
            {
                'event_id': 'event_001',
                'title': 'Совещание по проекту',
                'description': 'Обсуждение текущего прогресса проекта',
                'start_time': (now + timedelta(hours=2)).isoformat(),
                'end_time': (now + timedelta(hours=3)).isoformat(),
                'location': 'Конференц-зал А',
                'attendees': ['user1@company.com', 'user2@company.com'],
                'organizer': 'manager@company.com',
                'status': 'scheduled',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            },
            {
                'event_id': 'event_002',
                'title': 'Обучение новым технологиям',
                'description': 'Введение в новые инструменты разработки',
                'start_time': (now + timedelta(days=1)).isoformat(),
                'end_time': (now + timedelta(days=1, hours=3)).isoformat(),
                'location': 'Учебный класс Б',
                'attendees': ['dev1@company.com', 'dev2@company.com', 'dev3@company.com'],
                'organizer': 'trainer@company.com',
                'status': 'scheduled',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
        ]
        
        for event in sample_events:
            self.events_db[event['event_id']] = event
        
        print("Инициализированы тестовые события календаря")
    
    def validate_event_times(self, start_time: str, end_time: str) -> bool:
        """Проверяет корректность временных интервалов"""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            if end_dt <= start_dt:
                return False
                
            return True
        except (ValueError, TypeError):
            return False
    
    def check_time_conflicts(self, event_id: Optional[str], start_time: str, end_time: str, attendees: List[str]) -> List[str]:
        """Проверяет конфликты времени для участников"""
        conflicts = []
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        for existing_id, event in self.events_db.items():
            if event_id and existing_id == event_id:
                continue  # Пропускаем текущее событие при обновлении
                
            if event['status'] != 'scheduled':
                continue  # Пропускаем отмененные и завершенные события
                
            existing_start = datetime.fromisoformat(event['start_time'])
            existing_end = datetime.fromisoformat(event['end_time'])
            
            # Проверяем пересечение временных интервалов
            if not (end_dt <= existing_start or start_dt >= existing_end):
                # Проверяем пересечение участников
                common_attendees = set(attendees) & set(event['attendees'])
                if common_attendees:
                    conflicts.append(f"Конфликт с событием '{event['title']}' для участников: {', '.join(common_attendees)}")
        
        return conflicts
    
    def CreateEvent(self, request, context):
        """Создает новое событие в календаре"""
        print(f"Запрос на создание события: {request.title}")
        
        # Генерируем уникальный ID
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        
        # Валидация временных интервалов
        if not self.validate_event_times(request.start_time, request.end_time):
            return calendar_pb2.EventResponse(
                success=False,
                message="Некорректные временные интервалы. Конечное время должно быть после начального"
            )
        
        # Проверка конфликтов
        conflicts = self.check_time_conflicts(
            None, request.start_time, request.end_time, list(request.attendees)
        )
        
        if conflicts:
            conflict_msg = "; ".join(conflicts)
            return calendar_pb2.EventResponse(
                success=False,
                message=f"Обнаружены конфликты расписания: {conflict_msg}"
            )
        
        # Создаем событие
        now = datetime.now().isoformat()
        event_data = {
            'event_id': event_id,
            'title': request.title,
            'description': request.description,
            'start_time': request.start_time,
            'end_time': request.end_time,
            'location': request.location,
            'attendees': list(request.attendees),
            'organizer': request.organizer,
            'status': 'scheduled',
            'created_at': now,
            'updated_at': now
        }
        
        # Сохраняем в базу
        self.events_db[event_id] = event_data
        
        print(f"Событие создано: {event_id} - {request.title}")
        
        # Создаем ответ
        event_response = calendar_pb2.EventDetails(
            event_id=event_id,
            title=request.title,
            description=request.description,
            start_time=request.start_time,
            end_time=request.end_time,
            location=request.location,
            attendees=request.attendees,
            organizer=request.organizer,
            status='scheduled',
            created_at=now,
            updated_at=now
        )
        
        return calendar_pb2.EventResponse(
            success=True,
            message="Событие успешно создано",
            event=event_response
        )
    
    def GetEvent(self, request, context):
        """Получает информацию о событии"""
        print(f"Запрос на получение события: {request.event_id}")
        
        if request.event_id not in self.events_db:
            return calendar_pb2.EventDetails(
                event_id=request.event_id,
                title="",
                description="Событие не найдено",
                status="not_found"
            )
        
        event = self.events_db[request.event_id]
        
        return calendar_pb2.EventDetails(
            event_id=event['event_id'],
            title=event['title'],
            description=event['description'],
            start_time=event['start_time'],
            end_time=event['end_time'],
            location=event['location'],
            attendees=event['attendees'],
            organizer=event['organizer'],
            status=event['status'],
            created_at=event['created_at'],
            updated_at=event['updated_at']
        )
    
    def UpdateEvent(self, request, context):
        """Обновляет существующее событие"""
        print(f"Запрос на обновление события: {request.event_id}")
        
        if request.event_id not in self.events_db:
            return calendar_pb2.EventResponse(
                success=False,
                message="Событие не найдено"
            )
        
        # Валидация временных интервалов
        if not self.validate_event_times(request.start_time, request.end_time):
            return calendar_pb2.EventResponse(
                success=False,
                message="Некорректные временные интервалы"
            )
        
        # Проверка конфликтов (исключая текущее событие)
        conflicts = self.check_time_conflicts(
            request.event_id, request.start_time, request.end_time, list(request.attendees)
        )
        
        if conflicts:
            conflict_msg = "; ".join(conflicts)
            return calendar_pb2.EventResponse(
                success=False,
                message=f"Обнаружены конфликты расписания: {conflict_msg}"
            )
        
        # Обновляем событие
        event = self.events_db[request.event_id]
        event.update({
            'title': request.title,
            'description': request.description,
            'start_time': request.start_time,
            'end_time': request.end_time,
            'location': request.location,
            'attendees': list(request.attendees),
            'organizer': request.organizer,
            'updated_at': datetime.now().isoformat()
        })
        
        print(f"Событие обновлено: {request.event_id} - {request.title}")
        
        # Создаем ответ
        event_response = calendar_pb2.EventDetails(
            event_id=event['event_id'],
            title=event['title'],
            description=event['description'],
            start_time=event['start_time'],
            end_time=event['end_time'],
            location=event['location'],
            attendees=event['attendees'],
            organizer=event['organizer'],
            status=event['status'],
            created_at=event['created_at'],
            updated_at=event['updated_at']
        )
        
        return calendar_pb2.EventResponse(
            success=True,
            message="Событие успешно обновлено",
            event=event_response
        )
    
    def DeleteEvent(self, request, context):
        """Удаляет событие"""
        print(f"Запрос на удаление события: {request.event_id}")
        
        if request.event_id not in self.events_db:
            return calendar_pb2.EventResponse(
                success=False,
                message="Событие не найдено"
            )
        
        event_title = self.events_db[request.event_id]['title']
        del self.events_db[request.event_id]
        
        print(f"Событие удалено: {request.event_id} - {event_title}")
        
        return calendar_pb2.EventResponse(
            success=True,
            message=f"Событие '{event_title}' успешно удалено"
        )
    
    def ListEvents(self, request, context):
        """Возвращает список событий по фильтру"""
        print("Запрос на список событий с фильтром")
        
        filtered_events = []
        
        for event in self.events_db.values():
            # Применяем фильтры
            matches = True
            
            if request.start_date:
                event_start = datetime.fromisoformat(event['start_time']).date()
                filter_start = datetime.fromisoformat(request.start_date).date()
                if event_start < filter_start:
                    matches = False
            
            if matches and request.end_date:
                event_start = datetime.fromisoformat(event['start_time']).date()
                filter_end = datetime.fromisoformat(request.end_date).date()
                if event_start > filter_end:
                    matches = False
            
            if matches and request.organizer and event['organizer'] != request.organizer:
                matches = False
            
            if matches and request.status and event['status'] != request.status:
                matches = False
            
            if matches:
                filtered_events.append(calendar_pb2.EventDetails(
                    event_id=event['event_id'],
                    title=event['title'],
                    description=event['description'],
                    start_time=event['start_time'],
                    end_time=event['end_time'],
                    location=event['location'],
                    attendees=event['attendees'],
                    organizer=event['organizer'],
                    status=event['status'],
                    created_at=event['created_at'],
                    updated_at=event['updated_at']
                ))
        
        print(f"Найдено событий: {len(filtered_events)}")
        
        return calendar_pb2.EventList(
            events=filtered_events,
            total_count=len(filtered_events)
        )

def serve():
    """Запускает gRPC сервер календаря"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calendar_pb2_grpc.add_CalendarServiceServicer_to_server(CalendarServicer(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    
    print("Сервер CalendarService запущен на порту 50054")
    print("Доступные методы:")
    print("  - CreateEvent: создание нового события")
    print("  - GetEvent: получение информации о событии")
    print("  - UpdateEvent: обновление события")
    print("  - DeleteEvent: удаление события")
    print("  - ListEvents: список событий с фильтрацией")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("Сервер остановлен")

if __name__ == '__main__':
    serve()