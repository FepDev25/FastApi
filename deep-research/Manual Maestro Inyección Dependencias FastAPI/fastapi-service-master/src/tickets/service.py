from fastapi import Depends, HTTPException, status
from src.tickets.repository import TicketRepository
from src.tickets.models import Ticket
from src.tickets.schemas import TicketCreate, TicketUpdate

class TicketService:
    """Capa de servicio: Contiene la lógica de negocio"""
    
    def __init__(self, repo: TicketRepository = Depends()):
        self.repo = repo

    async def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        """Crear un ticket con lógica de negocio"""
        # Lógica de negocio: Auto-asignar prioridad alta si es crítico
        priority = ticket_data.priority
        if "CRITICAL" in ticket_data.title.upper() or "URGENTE" in ticket_data.title.upper():
            priority = 5
        
        # Crear instancia del modelo de base de datos
        ticket_db = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            priority=priority
        )
        
        return await self.repo.create(ticket_db)
    
    async def get_ticket(self, ticket_id: int) -> Ticket:
        """Obtener un ticket por ID"""
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found"
            )
        return ticket
    
    async def get_all_tickets(self, skip: int = 0, limit: int = 100) -> list[Ticket]:
        """Obtener todos los tickets con paginación"""
        return await self.repo.get_all(skip=skip, limit=limit)
    
    async def update_ticket(self, ticket_id: int, ticket_data: TicketUpdate) -> Ticket:
        """Actualizar un ticket"""
        ticket = await self.get_ticket(ticket_id)
        
        # Actualizar solo los campos proporcionados
        update_data = ticket_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        return await self.repo.update(ticket)
    
    async def delete_ticket(self, ticket_id: int) -> None:
        """Eliminar un ticket"""
        ticket = await self.get_ticket(ticket_id)
        await self.repo.delete(ticket)
        
