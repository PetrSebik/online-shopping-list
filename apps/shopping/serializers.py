from rest_framework.serializers import ModelSerializer
from apps.shopping.models import Item


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = (
            "id",
            "name",
            "quantity",
        )
