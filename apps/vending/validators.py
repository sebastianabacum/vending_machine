from rest_framework import serializers


class ListSlotsValidator(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=0, default=None)
