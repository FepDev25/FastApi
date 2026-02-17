from typing import Annotated
from fastapi import APIRouter, Depends, status, Query
from src.tickets.schemas import TicketCreate, TicketRead, TicketUpdate
from src.tickets.service import TicketService

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)

# Alias para inyectar el servicio - Dependency Injection
TicketServiceDep = Annotated[TicketService, Depends()]

@router.post( "/", response_model=TicketRead, status_code=status.HTTP_201_CREATED, summary="Create a new ticket")
async def create_ticket( ticket_in: TicketCreate, service: TicketServiceDep ) -> TicketRead:
    """Crear un nuevo ticket. Si el título contiene 'CRITICAL' o 'URGENTE', se asigna prioridad 5 automáticamente."""
    return await service.create_ticket(ticket_in)

@router.get("/", response_model=list[TicketRead], summary="Get all tickets")
async def get_all_tickets(service: TicketServiceDep, skip: int = Query(default=0, ge=0, description="Número de registros a saltar"), limit: int = Query(default=100, ge=1, le=100, description="Número máximo de registros a retornar")) -> list[TicketRead]:
    """Obtener todos los tickets con paginación."""
    return await service.get_all_tickets(skip=skip, limit=limit)

@router.get("/{ticket_id}", response_model=TicketRead, summary="Get a ticket by ID")
async def get_ticket(ticket_id: int, service: TicketServiceDep) -> TicketRead:
    """Obtener un ticket específico por su ID."""
    return await service.get_ticket(ticket_id)

@router.put("/{ticket_id}", response_model=TicketRead, summary="Update a ticket")
async def update_ticket(ticket_id: int, ticket_in: TicketUpdate, service: TicketServiceDep) -> TicketRead:
    """Actualizar un ticket existente. Solo se actualizan los campos proporcionados."""
    return await service.update_ticket(ticket_id, ticket_in)

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a ticket")
async def delete_ticket(ticket_id: int, service: TicketServiceDep) -> None:
    """Eliminar un ticket."""
    await service.delete_ticket(ticket_id)
