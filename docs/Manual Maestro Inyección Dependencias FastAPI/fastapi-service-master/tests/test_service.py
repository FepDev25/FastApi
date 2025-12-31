# Tests para la capa de Service.
# Prueba la lógica de negocio de la aplicación.

import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException

from src.tickets.models import Ticket
from src.tickets.schemas import TicketCreate, TicketUpdate
from src.tickets.service import TicketService
from src.tickets.repository import TicketRepository


class TestTicketService:
    # Tests para TicketService
    
    @pytest.mark.asyncio
    async def test_create_ticket_normal_priority(self, sample_ticket_data):
        # Test: Crear ticket con prioridad normal
        # Arrange
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.create = AsyncMock(return_value=Ticket(
            id=1,
            **sample_ticket_data
        ))
        
        service = TicketService(repo=mock_repo)
        ticket_create = TicketCreate(**sample_ticket_data)
        
        # Act
        result = await service.create_ticket(ticket_create)
        
        # Assert
        assert result.title == sample_ticket_data["title"]
        assert result.priority == sample_ticket_data["priority"]
        mock_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_ticket_critical_auto_priority(self):
        # Test: Crear ticket con palabra CRITICAL - prioridad automática a 5
        # Arrange
        mock_repo = Mock(spec=TicketRepository)
        
        async def mock_create(ticket):
            ticket.id = 1
            return ticket
        
        mock_repo.create = AsyncMock(side_effect=mock_create)
        
        service = TicketService(repo=mock_repo)
        ticket_data = TicketCreate(
            title="CRITICAL: Server down",
            description="Production server is offline",
            priority=2  # Esto será overrideado
        )
        
        # Act
        result = await service.create_ticket(ticket_data)
        
        # Assert
        assert result.priority == 5  # Auto-asignado
        mock_repo.create.assert_called_once()
        
        # Verificar que se llamó con prioridad 5
        call_args = mock_repo.create.call_args[0][0]
        assert call_args.priority == 5
    
    @pytest.mark.asyncio
    async def test_create_ticket_urgente_auto_priority(self):
        # Test: Crear ticket con palabra URGENTE - prioridad automática a 5
        # Arrange
        mock_repo = Mock(spec=TicketRepository)
        
        async def mock_create(ticket):
            ticket.id = 1
            return ticket
        
        mock_repo.create = AsyncMock(side_effect=mock_create)
        
        service = TicketService(repo=mock_repo)
        ticket_data = TicketCreate(
            title="URGENTE: Fix payment bug",
            description="Customers can't pay",
            priority=1
        )
        
        # Act
        result = await service.create_ticket(ticket_data)
        
        # Assert
        assert result.priority == 5
    
    @pytest.mark.asyncio
    async def test_get_ticket_existing(self):
        # Test: Obtener un ticket existente
        # Arrange
        ticket_id = 1
        mock_ticket = Ticket(
            id=ticket_id,
            title="Test",
            description="Test desc",
            priority=3
        )
        
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=mock_ticket)
        
        service = TicketService(repo=mock_repo)
        
        # Act
        result = await service.get_ticket(ticket_id)
        
        # Assert
        assert result.id == ticket_id
        assert result.title == "Test"
        mock_repo.get_by_id.assert_called_once_with(ticket_id)
    
    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self):
        # Test: Intentar obtener un ticket que no existe - debe lanzar 404
        # Arrange
        ticket_id = 99999
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        service = TicketService(repo=mock_repo)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.get_ticket(ticket_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_get_all_tickets(self):
        # Test: Obtener todos los tickets con paginación
        # Arrange
        mock_tickets = [
            Ticket(id=1, title="T1", description="D1", priority=1),
            Ticket(id=2, title="T2", description="D2", priority=2),
        ]
        
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_all = AsyncMock(return_value=mock_tickets)
        
        service = TicketService(repo=mock_repo)
        
        # Act
        result = await service.get_all_tickets(skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        mock_repo.get_all.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_update_ticket(self):
        # Test: Actualizar un ticket existente
        # Arrange
        ticket_id = 1
        existing_ticket = Ticket(
            id=ticket_id,
            title="Old Title",
            description="Old desc",
            priority=2,
            is_completed=False
        )
        
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=existing_ticket)
        mock_repo.update = AsyncMock(return_value=existing_ticket)
        
        service = TicketService(repo=mock_repo)
        
        update_data = TicketUpdate(
            title="New Title",
            is_completed=True
        )
        
        # Act
        result = await service.update_ticket(ticket_id, update_data)
        
        # Assert
        assert result.title == "New Title"
        assert result.is_completed is True
        assert result.description == "Old desc"  # No cambió
        mock_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_ticket_not_found(self):
        # Test: Intentar actualizar un ticket que no existe
        # Arrange
        ticket_id = 99999
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        service = TicketService(repo=mock_repo)
        update_data = TicketUpdate(title="New Title")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.update_ticket(ticket_id, update_data)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_ticket(self):
        # Test: Eliminar un ticket existente
        # Arrange
        ticket_id = 1
        existing_ticket = Ticket(
            id=ticket_id,
            title="To Delete",
            description="Will be deleted",
            priority=1
        )
        
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=existing_ticket)
        mock_repo.delete = AsyncMock(return_value=None)
        
        service = TicketService(repo=mock_repo)
        
        # Act
        await service.delete_ticket(ticket_id)
        
        # Assert
        mock_repo.delete.assert_called_once_with(existing_ticket)
    
    @pytest.mark.asyncio
    async def test_delete_ticket_not_found(self):
        # Test: Intentar eliminar un ticket que no existe
        # Arrange
        ticket_id = 99999
        mock_repo = Mock(spec=TicketRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        service = TicketService(repo=mock_repo)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_ticket(ticket_id)
        
        assert exc_info.value.status_code == 404
