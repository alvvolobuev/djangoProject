from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import BooleanField
from rest_framework.serializers import Serializer, ListField, ChoiceField

from .models import Notebook


class UserSerializer(serializers.ModelSerializer):
    """ Автор заметки """
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined')


class NotebookListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    date_add = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Notebook
        fields = "__all__"


class FilterSerializer(Serializer):
    activity = ListField(child=ChoiceField(choices=Notebook.ACTIVITY_STATUS), required=False)
    important = BooleanField(required=False)
    public = BooleanField(required=False)


class NoteIdSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Notebook
        exclude = ('public',)
        read_only_fields = ['date_add', 'user', ]
