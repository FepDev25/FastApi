"""
Tests para configuración y dependencias.
Prueba que las dependencias se inyecten correctamente.
"""

import pytest
from src.config import get_settings, Settings


class TestConfiguration:
    # Tests para la configuración de la aplicación
    
    def test_get_settings_returns_settings_instance(self):
        # Test: get_settings retorna una instancia de Settings
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_get_settings_is_cached(self):
        # Test: get_settings usa caché (lru_cache)
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Debe ser la misma instancia (mismo objeto en memoria)
        assert settings1 is settings2
    
    def test_settings_has_required_fields(self):
        # Test: Settings tiene todos los campos requeridos
        settings = get_settings()
        
        assert hasattr(settings, "APP_NAME")
        assert hasattr(settings, "VERSION")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "ALGORITHM")
        assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")
        assert hasattr(settings, "DEBUG_MODE")
    
    def test_settings_default_values(self):
        # Test: Valores por defecto de Settings
        settings = get_settings()
        
        assert settings.APP_NAME == "ServiceMaster API"
        assert settings.VERSION == "1.0.0"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
