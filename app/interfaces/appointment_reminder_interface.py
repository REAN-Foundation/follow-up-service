from abc import ABC, abstractmethod

class AppointmentReminderI(ABC):
    @abstractmethod
    async def create_reminder(self):pass

    @abstractmethod
    async def create_reports(self):pass

    @abstractmethod
    async def get_schedule_create_model(self):pass

    @abstractmethod
    async def schedule_reminder(self):pass

    