from _decimal import Decimal
from datetime import datetime
from django import forms

import pytest
from factory.django import DjangoModelFactory

from apps.vending.models import Product


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = "Snickers Bar"
    price = Decimal("10.40")
    created_at = datetime(2023, 5, 30, 12)
    updated_at = datetime(2023, 5, 30, 23)


@pytest.fixture
def product_pepino():
    return ProductFactory(name="pepino")


@pytest.fixture
def multiple_products():
    return [
        ProductFactory(name="pepino"),
        ProductFactory(name="chocolate"),
        ProductFactory(name="coca cola"),
    ]


@pytest.fixture
def products():
    return []


@pytest.mark.django_db
def test_default_only(products, product_pepino):
    assert products == [product_pepino]


@pytest.mark.django_db
def test_default_multiple_products(multiple_products):
    assert len(multiple_products) == 3

    # Fixtures can depend on other fixtures even if they're not autoused


@pytest.fixture(autouse=True)
def always_non_empty_products(products, product_pepino):
    return products.append(product_pepino)


# Notice that we did not explicitly list `always_non_empty_products` as a
# dependency
@pytest.mark.django_db
def test_multiple_products(products, product_pepino):
    wasabi = ProductFactory(name="Wasabi")
    products.append(wasabi)
    assert products == [product_pepino, wasabi]


@pytest.mark.django_db
def test_product_creation():
    test_product = ProductFactory(name="Heidi chocolate", price=Decimal("5.32"))

    stored_product = Product.objects.get(id=test_product.id)

    assert stored_product == test_product
    assert stored_product.price == Decimal("5.32")
    assert stored_product.name == "Heidi chocolate"


# @pytest.mark.django_db
# class TestProductValidators:
#     @pytest.mark.parametrize(
#         "price, expected",
#         [
#             (Decimal("-5.32"), 4),
#         ],
#         ids=["negative_price"],
#     )
#     @pytest.mark.django_db
#     def test_product_creation_validators(self, price, expected):
#         with pytest.raises(
#             forms.ValidationError,
#             match="Code 'SUM' is part of Abacum's grammar and cannot be used",
#         ):
#             Product.objects.create(name="chocolate", price=price)
