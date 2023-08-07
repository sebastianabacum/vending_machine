from django import forms
from apps.vending.tests.unit.product_tests import ProductFactory

import pytest
import factory
from factory.django import DjangoModelFactory

from apps.vending.models import VendingMachineSlot


class VendingMachineSlotFactory(DjangoModelFactory):
    class Meta:
        model = VendingMachineSlot

    product = factory.SubFactory(ProductFactory)
    quantity = 3
    row = 1
    column = 1


# This annotation (see more in section 3) is required because factories
# inheriting from DjangoModelFactory will be stored in the db.
# You can prevent this by calling the .build() method instead of
# the constructor (ProductFactory.build(name="Heidi chocolate"))
@pytest.mark.django_db
def test_vending_machine_slot_creation():
    test_vending_machine_slot = VendingMachineSlotFactory()

    stored_vending_machine_slot = VendingMachineSlot.objects.get(
        id=test_vending_machine_slot.id
    )

    assert stored_vending_machine_slot == test_vending_machine_slot
    assert stored_vending_machine_slot.quantity == 3


# @pytest.mark.django_db
# class TestProductValidators:
#     @pytest.mark.parametrize(
#         "slot",
#         [
#             (-1),
#             (-2),
#             (-3),
#         ],
#         ids=["slot 1", "slot 2", "slot 3"],
#     )
#     @pytest.mark.django_db
#     def test_product_creation_validators(self, slot):
#         product = ProductFactory(name="chocolate")
#         with pytest.raises(
#             forms.ValidationError,
#             match="Code 'SUM' is part of Abacum's grammar and cannot be used",
#         ):
#             VendingMachineSlot.objects.create(
#                 row=slot, column=slot, quantity=2, product=product
#             )
