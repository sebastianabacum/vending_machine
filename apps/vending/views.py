from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest

# from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vending.models import Buyer, VendingMachineSlot
from apps.vending.serializers import VendingMachineSlotSerializer
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
        amount = request.POST["amount"]
        buyer = Buyer.objects.filter(id=request.user.id).all()[0]
        if buyer is None:
            return HttpResponseBadRequest(content="user not logged in")

        current_amount = float(buyer.credit)
        new_amount = current_amount + float(amount)

        if new_amount < 0:
            return HttpResponseBadRequest(content="cannot have negative salary")

        buyer.credit = Decimal(new_amount)
        buyer.save()

        return Response(data={"success": True})


class BuyerRefundView(APIView):
    def post(self, request, *args, **kwargs):
        buyer = Buyer.objects.filter(id=request.user.id).all()[0]
        if buyer is None:
            return HttpResponseBadRequest(content="user not logged in")

        current_amount = float(buyer.credit)

        buyer.credit = Decimal("0.00")
        buyer.save()

        return Response(data={"success": True, "refund": current_amount})


class ProfileView(APIView):
    def get(self, request: Request) -> Response:
        if request.user.is_authenticated:
            return Response(data=request.user)


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("/vending-machine")
        else:
            return redirect("/")


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        logout(request)
        return redirect("/")
