from django.conf import settings

from .models import Company, JobApplication, JobReference

from rest_framework import serializers


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Company model.

    Fields:
        creator: User who created this company object
        references: Job references who work for this company

    Metaclass Fields:
        model: model to be serialized
        fields: fields to include in serialization

    Methods:

    References:
    """
    creator = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='user-detail',
        read_only=True
    )

    references = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='jobreference-detail',
        read_only=True
    )

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'website', 'creator',
            'job_applications', 'references'
        )


class JobReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Job Reference model.

    Fields:
        creator: User who created this job reference
        company: Company at which this person can provide a reference

    Metaclass Fields:
        model: Model to serialize
        fields: fields to include in serialization

    Methods:

    References:
    """

    creator = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='user-detail',
        read_only=True
    )

    company = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='company-detail',
        read_only=True
    )

    class Meta:
        model = JobReference
        fields = (
            'id', 'name', 'email', 'company', 'creator',
        )


class JobApplicationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for JobApplication model.

    Fields:
        company: Company application is directed towards
        creator: User who created this Job Application


    Metaclass Fields:
        model: Model to serialize (Job Application)
        fields: fields to include in serialization

    Methods:

    References:
    """

    company = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='company-detail',
        read_only=True
    )

    creator = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='user-detail',
        read_only=True
    )

    class Meta:
        model = JobApplication
        fields = (
            'id', 'company', 'creator', 'position', 'city', 'state', 'status',
            'submitted_date', 'updated_date', 'interview_date', 'rejected_date',
            'rejected_reason', 'rejected_state'
        )
