import random
import datetime
from datetime import datetime

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import CollectionRevision

import logging

logger = logging.getLogger(__name__)

from .models import Order, Consignment, CollectionEntries, Remark, CollectionRevision
from user.serializer import UserInfoSerializer
from digitalplatformbackend.constants import company_constants


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class ConsignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consignment
        fields = '__all__'
        read_only_fields = ('consignment_id',)

    def create(self, validated_data):
        rand = random.randint(1000, 9999)
        datetime_var = datetime.now()
        complex_num = rand + int(datetime_var.strftime("%Y")) + int(datetime_var.strftime("%m")) + int(
            datetime_var.strftime("%d")) + int(
            datetime_var.strftime("%H")) + int(datetime_var.strftime("%S"))
        validated_data['consignment_id'] = complex_num
        logger.info(f'consignment created Successfilly =  {complex_num}')
        return Consignment.objects.create(**validated_data)


class CollectionEntriesSerializer(serializers.ModelSerializer):
    collection_entry_id = serializers.CharField(required=False)

    class Meta:
        model = CollectionEntries
        fields = '__all__'
        read_only_fields = ('collected_by', 'company', 'consignment')

    def create(self, validated_data):
        validated_data['consignment_id'] = self.context['consignment']
        validated_data['company'] = self.context['company_id']
        print('abc', self.context['user'].company)
        validated_data['collected_by'] = self.context['user']
        collection_entries = CollectionEntries.objects.create(**validated_data)
        return collection_entries


class RemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remark
        fields = '__all__'


class CollectionGetEntriesSerializer(serializers.ModelSerializer):
    consignment = ConsignmentSerializer()
    weight = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    collected_by = UserInfoSerializer()
    dispatch_date = serializers.SerializerMethodField()
    remark_consignment = serializers.SerializerMethodField()

    class Meta:
        model = CollectionEntries
        fields = '__all__'

    def get_remark_consignment(self, obj):
        try:
            return Remark.objects.get(consignment_id=obj.consignment_id).remark
        except Remark.DoesNotExist:
            return "Not Remarked Yet"

    def get_weight(self, obj):
        weight = str(obj.weight) + " kg"
        logger.info(f"convert weight {obj.weight} to {weight} for Collection Entry")
        return weight

    def get_dispatch_date(self, obj):
        date_time = datetime.strftime(obj.dispatch_date, '%d-%m-%Y %H:%M:%S')
        logger.info(f"convert weight {obj.dispatch_date} to {date_time} for Collection Entry")
        return date_time

    def get_order_number(self, obj):
        order_number = obj.consignment.order_number.order_number
        logger.info(f"merge order number = {order_number} for Collection Entry ")
        return order_number


class ConsignmentGetSerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField()

    def get_order_number(self, obj):
        order_number = obj.order_number.order_number
        logger.info(f"merge order number = {order_number} for Collection Entry ")
        return order_number

    class Meta:
        model = Consignment
        fields = '__all__'


class ConsignmentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consignment
        fields = '__all__'
