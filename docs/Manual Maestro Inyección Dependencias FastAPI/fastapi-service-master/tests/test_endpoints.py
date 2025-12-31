"""
Tests de integración para los endpoints de la API.
Prueba el flujo completo: Router → Service → Repository → Database.
"""

import pytest
from httpx import AsyncClient

from src.tickets.models import Ticket


class TestTicketEndpoints:
    # Tests de integración para endpoints de tickets
    
    @pytest.mark.asyncio
    async def test_create_ticket(self, client: AsyncClient, sample_ticket_data):
        # Test: POST /tickets/ - Crear un nuevo ticket
        # Act
        response = await client.post("/tickets/", json=sample_ticket_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_ticket_data["title"]
        assert data["description"] == sample_ticket_data["description"]
        assert data["priority"] == sample_ticket_data["priority"]
        assert data["is_completed"] is False
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_ticket_critical_auto_priority(self, client: AsyncClient):
        # Test: Crear ticket con CRITICAL - prioridad automática a 5
        # Arrange
        ticket_data = {
            "title": "CRITICAL: Production server crashed",
            "description": "All services are down",
            "priority": 2
        }
        
        # Act
        response = await client.post("/tickets/", json=ticket_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == 5  # Auto-asignado
        assert "CRITICAL" in data["title"]
    
    @pytest.mark.asyncio
    async def test_create_ticket_validation_error(self, client: AsyncClient):
        # Test: Crear ticket con datos inválidos - validación Pydantic
        # Arrange
        invalid_data = {
            "title": "",  # Vacío - inválido
            "description": "Test"
        }
        
        # Act
        response = await client.post("/tickets/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation Error
    
    @pytest.mark.asyncio
    async def test_get_ticket_by_id(self, client: AsyncClient, sample_ticket_data):
        # Test: GET /tickets/{id} - Obtener un ticket por ID
        # Arrange - Crear ticket primero
        create_response = await client.post("/tickets/", json=sample_ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Act
        response = await client.get(f"/tickets/{ticket_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket_id
        assert data["title"] == sample_ticket_data["title"]
    
    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self, client: AsyncClient):
        # Test: GET /tickets/{id} con ID inexistente - 404
        # Act
        response = await client.get("/tickets/99999")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_all_tickets_empty(self, client: AsyncClient):
        # Test: GET /tickets/ - Lista vacía cuando no hay tickets
        # Act
        response = await client.get("/tickets/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_tickets(self, client: AsyncClient):
        # Test: GET /tickets/ - Obtener todos los tickets
        # Arrange - Crear varios tickets
        tickets_data = [
            {"title": "Bug 1", "description": "Desc 1", "priority": 3},
            {"title": "Bug 2", "description": "Desc 2", "priority": 1},
            {"title": "Feature", "description": "Desc 3", "priority": 2},
        ]
        
        for ticket_data in tickets_data:
            await client.post("/tickets/", json=ticket_data)
        
        # Act
        response = await client.get("/tickets/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in ticket for ticket in data)
    
    @pytest.mark.asyncio
    async def test_get_all_tickets_pagination(self, client: AsyncClient):
        # Test: GET /tickets/ con paginación
        # Arrange - Crear 5 tickets
        for i in range(5):
            await client.post("/tickets/", json={
                "title": f"Ticket {i}",
                "description": f"Description {i}",
                "priority": 1
            })
        
        # Act - Primera página (2 items)
        response1 = await client.get("/tickets/?skip=0&limit=2")
        # Segunda página (2 items)
        response2 = await client.get("/tickets/?skip=2&limit=2")
        # Tercera página (1 item)
        response3 = await client.get("/tickets/?skip=4&limit=2")
        
        # Assert
        assert response1.status_code == 200
        assert len(response1.json()) == 2
        
        assert response2.status_code == 200
        assert len(response2.json()) == 2
        
        assert response3.status_code == 200
        assert len(response3.json()) == 1
    
    @pytest.mark.asyncio
    async def test_update_ticket(self, client: AsyncClient, sample_ticket_data):
        # Test: PUT /tickets/{id} - Actualizar un ticket
        # Arrange - Crear ticket
        create_response = await client.post("/tickets/", json=sample_ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Act - Actualizar
        update_data = {
            "title": "Updated Title",
            "is_completed": True,
            "priority": 5
        }
        response = await client.put(f"/tickets/{ticket_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["is_completed"] is True
        assert data["priority"] == 5
        # Description no cambió
        assert data["description"] == sample_ticket_data["description"]
    
    @pytest.mark.asyncio
    async def test_update_ticket_partial(self, client: AsyncClient, sample_ticket_data):
        # Test: Actualización parcial - solo algunos campos
        # Arrange
        create_response = await client.post("/tickets/", json=sample_ticket_data)
        ticket_id = create_response.json()["id"]
        original_title = sample_ticket_data["title"]
        
        # Act - Solo actualizar is_completed
        update_data = {"is_completed": True}
        response = await client.put(f"/tickets/{ticket_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert data["title"] == original_title  # No cambió
        assert data["description"] == sample_ticket_data["description"]  # No cambió
    
    @pytest.mark.asyncio
    async def test_update_ticket_not_found(self, client: AsyncClient):
        # Test: Actualizar ticket inexistente - 404
        # Act
        update_data = {"title": "New Title"}
        response = await client.put("/tickets/99999", json=update_data)
        
        # Assert
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_ticket(self, client: AsyncClient, sample_ticket_data):
        # Test: DELETE /tickets/{id} - Eliminar un ticket
        # Arrange - Crear ticket
        create_response = await client.post("/tickets/", json=sample_ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Act - Eliminar
        response = await client.delete(f"/tickets/{ticket_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verificar que ya no existe
        get_response = await client.get(f"/tickets/{ticket_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_ticket_not_found(self, client: AsyncClient):
        #Test: Eliminar ticket inexistente - 404
        # Act
        response = await client.delete("/tickets/99999")
        
        # Assert
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_full_crud_flow(self, client: AsyncClient):
        # Test: Flujo completo CRUD
        # 1. CREATE
        create_data = {
            "title": "Integration Test Ticket",
            "description": "Testing full CRUD flow",
            "priority": 3
        }
        create_response = await client.post("/tickets/", json=create_data)
        assert create_response.status_code == 201
        ticket_id = create_response.json()["id"]
        
        # 2. READ
        get_response = await client.get(f"/tickets/{ticket_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == create_data["title"]
        
        # 3. UPDATE
        update_data = {"is_completed": True, "priority": 5}
        update_response = await client.put(f"/tickets/{ticket_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["is_completed"] is True
        
        # 4. DELETE
        delete_response = await client.delete(f"/tickets/{ticket_id}")
        assert delete_response.status_code == 204
        
        # 5. Verificar que ya no existe
        final_get = await client.get(f"/tickets/{ticket_id}")
        assert final_get.status_code == 404
