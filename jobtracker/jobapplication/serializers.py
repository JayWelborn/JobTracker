from django.conf import settings
from django.db import transaction

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
            'url', 'id', 'name', 'website', 'creator', 'job_applications',
            'references'
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
        read_only=False,
        queryset=Company.objects.all(),
    )

    class Meta:
        model = JobReference
        fields = (
            'url', 'id', 'name', 'email', 'company', 'creator',
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
        is_valid: Perform validation sp

    References:
    """

    company = CompanySerializer(many=False, read_only=False)

    creator = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='user-detail',
        read_only=True
    )

    update_method = serializers.CharField(max_length=18, required=False)

    class Meta:
        model = JobApplication
        fields = (
            'url', 'id', 'company', 'creator', 'position', 'city', 'state',
            'status', 'submitted_date', 'updated_date', 'interview_date',
            'rejected_date', 'rejected_reason', 'rejected_state',
            'update_method',
        )

    def validate_update_method(self, value):
        """
        Update methods that match transition methods in the JobApplication
        class are valid. Others are not.

        If update_method is `schedule_interview`, serializer must also include
        an `interview_date`

        If update_method is `reject`, serializer must also include a
        `rejected_reason`
        """
        if value not in JobApplication.VALID_UPDATE_METHODS:
            raise serializers.ValidationError("Invalid update method.")

        if value == 'schedule_interview' and \
                'interview_date' not in self.initial_data:
            raise serializers.ValidationError(
                "Cannot schedule interview without date")

        if value == 'reject' and 'rejected_reason' not in self.initial_data:
            raise serializers.ValidationError(
                "Cannot reject application without reason")

        return value

    def update(self, instance, validated_data):
        """
        This is where the magic happens. If `update_method` not provided,
        update normally. If `update_method` is provided, perform the model
        method with the corresponding name on the instance of JobApplication.

        :param instance:
        :param validated_data:
        :return:
        """

        # TODO write this method
