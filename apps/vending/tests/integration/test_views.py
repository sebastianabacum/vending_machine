from decimal import Decimal
from unittest.mock import ANY

import pytest
from rest_framework import status

from django.contrib.auth.models import User
import factory
from factory.django import DjangoModelFactory
from apps.vending.models import Buyer, Product, VendingMachineSlot
from apps.vending.tests.unit.product_tests import ProductFactory
from apps.vending.tests.unit.vending_machine_slot_tests import VendingMachineSlotFactory


@pytest.fixture
def products_list() -> list[Product]:
    return [ProductFactory(name=f"Product {i}") for i in range(1, 11)]


@pytest.fixture
def slots_grid(products_list) -> list[VendingMachineSlot]:
    """returns a grid of slots of 5x2"""
    slots = []
    for row in range(1, 3):
        for column in range(1, 6):
            slot = VendingMachineSlotFactory(
                product=products_list.pop(), row=row, column=column, quantity=column - 1
            )
            slots.append(slot)
    return slots


@pytest.mark.django_db
class TestListVendingMachineSlots:
    def test_list_slots_returns_expected_response(self, client, slots_grid):
        response = client.get("/slots/")

        expected_response = [
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 1],
                "product": {"id": ANY, "name": "Product 10", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 1],
                "product": {"id": ANY, "name": "Product 9", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 2,
                "coordinates": [3, 1],
                "product": {"id": ANY, "name": "Product 8", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 3,
                "coordinates": [4, 1],
                "product": {"id": ANY, "name": "Product 7", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 4,
                "coordinates": [5, 1],
                "product": {"id": ANY, "name": "Product 6", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 2],
                "product": {"id": ANY, "name": "Product 5", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 2],
                "product": {"id": ANY, "name": "Product 4", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 2,
                "coordinates": [3, 2],
                "product": {"id": ANY, "name": "Product 3", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 3,
                "coordinates": [4, 2],
                "product": {"id": ANY, "name": "Product 2", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 4,
                "coordinates": [5, 2],
                "product": {"id": ANY, "name": "Product 1", "price": "10.40"},
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

    @pytest.mark.django_db
    def test_list_slots_returns_filtered_response(self, client, slots_grid):
        response = client.get("/slots/?quantity=1")

        expected_response = [
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 1],
                "product": {"id": ANY, "name": "Product 10", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 1],
                "product": {"id": ANY, "name": "Product 9", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 2],
                "product": {"id": ANY, "name": "Product 5", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 2],
                "product": {"id": ANY, "name": "Product 4", "price": "10.40"},
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

    def test_invalid_quantity_filter_returns_bad_request(self, client):
        response = client.get("/slots/?quantity=-1")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "quantity": ["Ensure this value is greater than or equal to 0."]
        }


@pytest.mark.django_db
class TestBuyer:
    def test_buyer_login(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))

        response = client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "/vending-machine"

    def test_buyer_add_credit(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))

        login = client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        add_credit = client.post("/add-credit/", {"amount": 10})

        assert login.status_code == status.HTTP_302_FOUND
        assert add_credit.status_code == status.HTTP_200_OK

        assert Buyer.objects.all()[0].credit == Decimal("15.00")

    def test_buyer_refund(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))

        login = client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        add_credit = client.post("/add-credit/", {"amount": 10})
        assert Buyer.objects.all()[0].credit == Decimal("15.00")
        assert login.status_code == status.HTTP_302_FOUND
        assert add_credit.status_code == status.HTTP_200_OK

        refund = client.post("/refund/")
        assert refund.status_code == status.HTTP_200_OK
        assert Buyer.objects.all()[0].credit == Decimal("0.00")

    def test_buyer_order(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))
        test_vending_machine_slot = VendingMachineSlotFactory()

        client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        client.post("/add-credit/", {"amount": 20})
        assert Buyer.objects.all()[0].credit == Decimal("25.00")

        order = client.post(
            "/order/", {"slot_id": test_vending_machine_slot.id, "quantity": 2}
        )
        assert order.status_code == status.HTTP_200_OK
        assert Buyer.objects.all()[0].credit == Decimal("4.20")
        assert len(VendingMachineSlot.objects.all()) == 0

    def test_buyer_order_fails(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))
        test_vending_machine_slot = VendingMachineSlotFactory()

        client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        client.post("/add-credit/", {"amount": 5})
        assert Buyer.objects.all()[0].credit == Decimal("10.00")

        order = client.post(
            "/order/", {"slot_id": test_vending_machine_slot.id, "quantity": 2}
        )
        assert order.status_code == status.HTTP_400_BAD_REQUEST
        assert Buyer.objects.all()[0].credit == Decimal("10.00")
        assert len(VendingMachineSlot.objects.all()) == 1

    def test_buyer_logout(self, client):
        user = User.objects.create_user("jorge", "jorge@abacum.io", "password")
        Buyer.objects.create(user=user, credit=Decimal("5.00"))

        response = client.post(
            "/login/",
            {"username": "jorge", "password": "password"},
            Follow=True,
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "/vending-machine"

        response = client.post(
            "/logout/",
            Follow=True,
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "/"
