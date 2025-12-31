from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import get_db_session
from src.tickets.models import Ticket
from typing import List
from fastapi import Depends

class TicketRepository:
    """Capa de repositorio: Maneja el acceso a datos"""
    
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create(self, ticket: Ticket) -> Ticket:
        """Crear un nuevo ticket en la base de datos"""
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket
    
    async def get_by_id(self, ticket_id: int) -> Ticket | None:
        """Obtener un ticket por ID"""
        return await self.session.get(Ticket, ticket_id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Obtener todos los tickets con paginación"""
        statement = select(Ticket).offset(skip).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())
    
    async def update(self, ticket: Ticket) -> Ticket:
        """Actualizar un ticket existente"""
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket
    
    async def delete(self, ticket: Ticket) -> None:
        """Eliminar un ticket"""
        await self.session.delete(ticket)
        await self.session.commit()