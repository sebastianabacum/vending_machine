import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest

# from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vending.models import Buyer, VendingMachineSlot
from apps.vending.serializers import BuyerSerializer, VendingMachineSlotSerializer
from apps.vending.validators import ListSlotsValidator


class VendingMachineSlotsView(APIView):
    def get(self, request: Request) -> Response:
        validator = ListSlotsValidator(data=request.query_params)
        validator.is_valid(raise_exception=True)
        filters = {}
        if quantity := validator.validated_data["quantity"]:
            filters["quantity__lte"] = quantity

        slots = VendingMachineSlot.objects.filter(**filters)
        slots_serializer = VendingMachineSlotSerializer(slots, many=True)
        return Response(data=slots_serializer.data)


class VendingMachineSlotsMatrixView(APIView):
    def get(self, request: Request) -> Response:
        slots_matrix = [[None, None, None], [None, None, None], [None, None, None]]
        for row in range(0, 3):
            for column in range(0, 3):
                filters = {}
                filters["row"] = row
                filters["column"] = column
                slot = VendingMachineSlot.objects.filter(**filters)
                if slot is not None:
                    slots_serializer = VendingMachineSlotSerializer(slot, many=True)
                    if len(slots_serializer.data) > 0:
                        slots_matrix[row][column] = slots_serializer.data[0]
                    else:
                        slots_matrix[row][column] = None
                else:
                    slots_matrix[row][column] = None

        return Response(data=slots_matrix)


class VendingMachineSlotView(APIView):
    def get(self, request, *args, **kwargs):
        id = self.kwargs["id"]
        if id is not None:
            slot = VendingMachineSlot.objects.get(id=id)
            slots_serializer = VendingMachineSlotSerializer(slot)
        return Response(data=slots_serializer.data)


class BuyerCreditView(APIView):
    def post(self, request, *args, **kwargs):
        amount = request.data["amount"]
        buyer = Buyer.objects.filter(user=request.user).first()
        if buyer is None:
            return HttpResponseBadRequest(content="user not logged in")

        current_amount = float(buyer.credit)
        new_amount = current_amount + float(amount)

        if new_amount < 0:
            return HttpResponseBadRequest(content="cannot have negative salary")

        buyer.credit = Decimal(new_amount)
        buyer.save()

        return Response(data={"balance": new_amount})


class BuyerRefundView(APIView):
    def post(self, request, *args, **kwargs):
        buyer = Buyer.objects.filter(user=request.user).first()
        if buyer is None:
            return HttpResponseBadRequest(content="user not logged in")

        buyer.credit = Decimal("0.00")
        buyer.save()

        return Response(data={"balance": buyer.credit})


class BuyerOrderView(APIView):
    def post(self, request):
        slot_id = request.data["slot_id"]
        quantity = request.data["quantity"]
        vending_machine_slot = VendingMachineSlot.objects.filter(id=slot_id).first()
        buyer = Buyer.objects.filter(user=request.user).first()
        if buyer is None:
            return HttpResponseBadRequest(content="user not logged in")

        current_amount = float(buyer.credit)
        product_price = float(vending_machine_slot.product.price)
        total_product_price = int(quantity) * product_price

        if total_product_price > current_amount:
            return HttpResponseBadRequest(content="Money not enough to buy products")

        vending_machine_slot_quantity = vending_machine_slot.quantity
        if vending_machine_slot_quantity - quantity == 0:
            vending_machine_slot.delete()
        else:
            vending_machine_slot.quantity -= 1
            vending_machine_slot.save()

        buyer.credit = Decimal(current_amount - total_product_price)
        buyer.save()

        return Response(data={"balance": buyer.credit})


class ProfileView(APIView):
    def get(self, request: Request) -> Response:
        if request.user.is_authenticated:
            buyer = Buyer.objects.get(user=request.user)
            buyer_serializer = BuyerSerializer(buyer)
            return Response(data=buyer_serializer.data)


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        username = request.data["username"]
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(self.request, user)

            buyer = Buyer.objects.filter(user=user).first()
            if not buyer:
                buyer = Buyer.objects.create(user=user, credit=0)

            buyer_serializer = BuyerSerializer(buyer)
            return Response(
                data=buyer_serializer.data
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)
