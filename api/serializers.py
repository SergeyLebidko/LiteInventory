from rest_framework import serializers

from main.models import Group, EquipmentCard, EquipmentType, EquipmentFeature


class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        model = Group
        fields = ['id', 'title', 'group']


class EquipmentCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentCard
        fields = '__all__'


class EquipmentTypeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        model = EquipmentType
        fields = ['id', 'title']


class EquipmentFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentFeature
        fields = '__all__'
