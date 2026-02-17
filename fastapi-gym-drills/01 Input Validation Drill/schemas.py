from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, TYPE_CHECKING
from models import Package

class PackageSchema(BaseModel):
    weight: Annotated[float, Field(gt=0, lt=50, description="Weight of the package in kilograms")]
    destination: Annotated[str, Field(min_length=3, max_length=100, description="Destination address of the package")]
    tags: Annotated[set[str], Field(description="Set of tags associated with the package")]

    # Example configuration for documentation (Pydantic v2)
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weight": 2.5,
                    "destination": "123 Main St, Springfield",
                    "tags": ["fragile", "express"]
                }
            ]
        }
    )

    # Method to convert schema to model
    def to_model(self) -> Package:
        return Package(
            weight=self.weight,
            destination=self.destination,
            tags=self.tags
        )


class PackageResponse(BaseModel):
    # Schema para respuestas de Package
    weight: float
    destination: str
    tags: set[str]
    
    @classmethod
    def from_model(cls, package: Package) -> "PackageResponse":
        # Crea un PackageResponse desde un modelo Package
        return cls(
            weight=package.weight,
            destination=package.destination,
            tags=package.tags
        )


class PackageCreateResponse(BaseModel):
    # Schema para respuesta de creación de Package
    message: str
    package_details: PackageResponse


class PackageListResponse(BaseModel):
    # Schema para lista de Packages
    packages: list[PackageResponse]
