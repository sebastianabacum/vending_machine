from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.vending.models import VendingMachineSlot
from apps.vending.serializers import VendingMachineSlotSerializer


class VendingMachineSlotView(APIView):
    def get(self, request: Request) -> Response:
        slots = VendingMachineSlot.objects.all()
        slots_serializer = VendingMachineSlotSerializer(slots, many=True)
        return Response(data=slots_serializer.data)
