from django.contrib.auth.models import User

from rest_framework import serializers

from auth_extension.models import UserProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer to convert Users to various data types.

    Fields:
        cards: Reverse lookup field to find Bingo Cards related to a
               given user.
        profile: User's profile data
        model: model to be serialized
        fields: fields to include in serialization
        read_only_fields: specifies which fields can't be written to via API
        extra_kwargs:
            password: set password so it is write-only. No one should be
                allowed to see any user's password hash

    Methods:
        create: Upon creation, new User should have a blank profile associated
            with it.

    References:
        * http://www.django-rest-framework.org/tutorial/1-serialization/#using-Hyperlinkedmodelserializers

    """

    profile = serializers.HyperlinkedRelatedField(
        many=False, view_name='userprofile-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username',
                  'profile', 'email', 'password')
        read_only_fields = ('is_staff', 'is_superuser',
                            'is_active', 'date_joined',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """
        Create new User object, as well as an associated Profile Object
        with blank fields.
        """

        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'))
        return user

    def update(self, instance, validated_data):
        """
        Update passwords via `User.set_password` method. Update
        other fields normally.
        """

        if validated_data.get('username'):
            instance.username = validated_data.get('username')

        if validated_data.get('email'):
            instance.email = validated_data.get('email')

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))

        instance.save()
        return instance


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Seralizer for User Profiles.

    Fields:
        user: related User object
        model: model to be serialized
        fields: fields to include in serialization

    References:
            * http://www.django-rest-framework.org/tutorial/1-serialization/#using-Hyperlinkedmodelserializers

    """

    user = serializers.HyperlinkedRelatedField(
        many=False, view_name='user-detail', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'user', 'created_date', 'slug',)
        extra_kwargs = {
            'slug': {'read_only': True},
        }
