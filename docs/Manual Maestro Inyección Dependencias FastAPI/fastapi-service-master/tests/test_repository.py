# Tests para la capa de Repository.
# Prueba las operaciones CRUD directamente contra la base de datos.

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from src.tickets.models import Ticket
from src.tickets.repository import TicketRepository


class TestTicketRepository:
    # Tests para TicketRepository
    
    @pytest.mark.asyncio
    async def test_create_ticket(self, test_session: AsyncSession, sample_ticket_data):
        # Test: Crear un ticket en la base de datos
        # Arrange
        repo = TicketRepository(session=test_session)
        ticket = Ticket(**sample_ticket_data)
        
        # Act
        created_ticket = await repo.create(ticket)
        
        # Assert
        assert created_ticket.id is not None
        assert created_ticket.title == sample_ticket_data["title"]
        assert created_ticket.description == sample_ticket_data["description"]
        assert created_ticket.priority == sample_ticket_data["priority"]
        assert created_ticket.is_completed is False
    
    @pytest.mark.asyncio
    async def test_get_by_id_existing(self, test_session: AsyncSession, created_ticket):
        # Test: Obtener un ticket existente por ID
        # Arrange
        repo = TicketRepository(session=test_session)
        
        # Act
        found_ticket = await repo.get_by_id(created_ticket.id)
        
        # Assert
        assert found_ticket is not None
        assert found_ticket.id == created_ticket.id
        assert found_ticket.title == created_ticket.title
    
    @pytest.mark.asyncio
    async def test_get_by_id_non_existing(self, test_session: AsyncSession):
        # Test: Intentar obtener un ticket que no existe
        # Arrange
        repo = TicketRepository(session=test_session)
        non_existing_id = 99999
        
        # Act
        found_ticket = await repo.get_by_id(non_existing_id)
        
        # Assert
        assert found_ticket is None
    
    @pytest.mark.asyncio
    async def test_get_all_tickets(self, test_session: AsyncSession, multiple_tickets):
        # Test: Obtener todos los tickets
        # Arrange
        repo = TicketRepository(session=test_session)
        
        # Act
        tickets = await repo.get_all(skip=0, limit=100)
        
        # Assert
        assert len(tickets) == 3
        assert all(isinstance(t, Ticket) for t in tickets)
    
    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, test_session: AsyncSession, multiple_tickets):
        # Test: Obtener tickets con paginación
        # Arrange
        repo = TicketRepository(session=test_session)
        
        # Act
        first_page = await repo.get_all(skip=0, limit=2)
        second_page = await repo.get_all(skip=2, limit=2)
        
        # Assert
        assert len(first_page) == 2
        assert len(second_page) == 1
    
    @pytest.mark.asyncio
    async def test_update_ticket(self, test_session: AsyncSession, created_ticket):
        # Test: Actualizar un ticket existente
        # Arrange
        repo = TicketRepository(session=test_session)
        created_ticket.title = "Updated Title"
        created_ticket.is_completed = True
        
        # Act
        updated_ticket = await repo.update(created_ticket)
        
        # Assert
        assert updated_ticket.title == "Updated Title"
        assert updated_ticket.is_completed is True
        
        # Verificar en DB
        fetched = await repo.get_by_id(created_ticket.id)
        assert fetched.title == "Updated Title"
        assert fetched.is_completed is True
    
    @pytest.mark.asyncio
    async def test_delete_ticket(self, test_session: AsyncSession, created_ticket):
        # Test: Eliminar un ticket
        # Arrange
        repo = TicketRepository(session=test_session)
        ticket_id = created_ticket.id
        
        # Act
        await repo.delete(created_ticket)
        
        # Assert
        deleted_ticket = await repo.get_by_id(ticket_id)
        assert deleted_ticket is None
