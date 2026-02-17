from fastapi import FastAPI
from starlette import status
from schemas import (
    PackageSchema,
    PackageResponse,
    PackageCreateResponse,
    PackageListResponse
)
from models import Package

db = list[Package]()

app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Welcome to the Package API"}

@app.post("/packages/", status_code=status.HTTP_201_CREATED, response_model=PackageCreateResponse)
async def create_package(package: PackageSchema):
    package_model = package.to_model()
    db.append(package_model)
    return PackageCreateResponse(
        message="Package received",
        package_details=PackageResponse.from_model(package_model)
    )

@app.get("/packages/", status_code=status.HTTP_200_OK, response_model=PackageListResponse)
async def list_packages():
    return PackageListResponse(
        packages=[PackageResponse.from_model(pkg) for pkg in db]
    )