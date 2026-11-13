
from app.repositories.json_repository import JsonRepository
from app.services.year_service import YearService
from app.services.product_service import ProductService


def get_year_service() -> YearService:
    repository = JsonRepository()
    return YearService(repository=repository)


def get_product_service() -> ProductService:
    repository = JsonRepository()
    return ProductService(repository=repository)
