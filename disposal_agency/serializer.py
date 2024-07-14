from rest_framework import serializers

from .models import DisposalEntries, DisposalRevision
from transporter.models import Consignment
from transporter.models import Remark
from digitalplatformbackend.constants import company_constants
from user.serializer import UserInfoSerializer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DisposalEntriesSerializer(serializers.ModelSerializer):
    disposal_entry_id = serializers.CharField(required=False)

    class Meta:
        model = DisposalEntries
        fields = '__all__'
        read_only_fields = ('collected_by',)

    def create(self, validated_data):
        validated_data['collected_by'] = self.context['user']
        logger.info(f"Disposal Entry Created Successfully")
        validated_data['company'] = self.context['user'].company

        return DisposalEntries.objects.create(**validated_data)


class RemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remark
        fields = '__all__'


class DisposalGetEntriesSerializer(serializers.ModelSerializer):
    collected_by = UserInfoSerializer()
    weight = serializers.SerializerMethodField()
    unloading_date = serializers.SerializerMethodField()
    consignment = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    remark_consignment = serializers.SerializerMethodField()

    class Meta:
        model = DisposalEntries
        fields = '__all__'
        read_only_fields = ('collected_by',)

    def get_remark_consignment(self, obj):
        remark = ''
        try:
            remark = Remark.objects.get(consignment_id=obj.consignment_id)
            # if remark.remark_to == company_constants.collection_agency:
            #     remark_agency = "Collection Agency"
            # elif remark.remark_to == company_constants.disposal_agency:
            #     remark_agency = "Disposal Agency"
            # elif remark.remark_to == company_constants.Both_Agency:
            #     remark_agency = "Both Agency"
        except:
            pass
        if remark:
            return remark.remark
        else:
            return remark

    def get_weight(self, obj):
        weight = str(obj.weight) + " kg"
        logger.info(f"convert weight {obj.weight} to {weight} for Disposal Entry")
        return weight

    def get_unloading_date(self, obj):
        date_time = datetime.strftime(obj.unloading_date, '%d-%m-%Y %H:%M:%S')
        logger.info(f"convert Date format {obj.unloading_date} to {date_time} for Disposal Entry")
        return date_time

    def get_consignment(self, obj):
        logger.info(f"merge Consignament ID = {obj.consignment.consignment_id} for Disposal Entry ")
        return obj.consignment.consignment_id

    def get_order_number(self, obj):
        logger.info(f"merge order number = {obj.consignment.order_number.order_number} for Collection Entry ")
        return obj.consignment.order_number.order_number
