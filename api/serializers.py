from rest_framework import serializers

from main.models import Group


class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        model = Group
        fields = ['id', 'title', 'group']
