from django.conf import settings

from .models import Company, JobApplication, JobReference

from rest_framework import serializers


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Company model.

    Fields:
        model: model to be serialized
        fields: fields to include in serialization

    Methods:

    References:
    """
    creator = serializers.HyperlinkedRelatedField(
        many=False,
        # view_name='user-detail',
        read_only=True
    )

    class Meta:
        model = Company
        fields = ('id', 'name', 'website', 'creator')
