from django.db.models import Q
from django.shortcuts import render
from django.views import View
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoProject import settings_local
from .models import Notebook
from .serializers import NotebookListSerializer, NoteIdSerializer, FilterSerializer


class NotesView(APIView):
    """ Статьи для блога """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Получить статьи для блога """

        notes = Notebook.objects.filter(public=True).order_by('-date_add', 'important')
        filter_params = FilterSerializer(data=request.query_params)

        if not filter_params.is_valid():
            return Response(filter_params.errors, status=status.HTTP_400_BAD_REQUEST)
        q_filter = Q()
        if filter_params.data.get('activity'):

            for ac in filter_params.data['activity']:
                q_filter |= Q(activity=ac)
        # if filter_params.data.get('important') or not filter_params.data.get('important'):
        if 'important' in filter_params.data:
            q_filter &= Q(important=filter_params.data.get('important'))
        if 'public' in filter_params.data:
            q_filter &= Q(important=filter_params.data.get('public'))
        notes = notes.filter(q_filter)

        serializer = NotebookListSerializer(notes, many=True)

        return Response(serializer.data)

    def post(self, request):
        new_note = NotebookListSerializer(data=request.data)

        # Проверка параметров
        if new_note.is_valid():
            # Записываем новую статью и добавляем текущего пользователя как автора
            new_note.save(user=request.user)
            return Response(new_note.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_note.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, note_id):
        """ Получить статю """
        note = Notebook.objects.filter(pk=note_id).first()

        if not note:
            raise NotFound(f'Опубликованная статья с id={note_id} не найдена')

        serializer = NoteIdSerializer(note)
        return Response(serializer.data)

    def delete(self, request, note_id):
        """ Удалить комментарий """
        note = Notebook.objects.filter(pk=note_id).first()
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, note_id):
        note = Notebook.objects.filter(pk=note_id).first()
        if not note:
            raise NotFound(f'Опубликованная статья с id={note_id} не найдена')
        serializer = NoteIdSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotesUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        notes = Notebook.objects.filter(user=request.user).order_by('date_add', '-important')
        filter_params = FilterSerializer(data=request.query_params)

        if not filter_params.is_valid():
            return Response(filter_params.errors, status=status.HTTP_400_BAD_REQUEST)
        q_filter = Q()
        if filter_params.data.get('activity'):

            for ac in filter_params.data['activity']:
                q_filter |= Q(activity=ac)
        # if filter_params.data.get('important') or not filter_params.data.get('important'):
        if 'important' in filter_params.data:
            q_filter &= Q(important=filter_params.data.get('important'))
        if 'public' in filter_params.data:
            q_filter &= Q(important=filter_params.data.get('public'))
        notes = notes.filter(q_filter)

        serializer = NotebookListSerializer(notes, many=True)

        return Response(serializer.data)


class AboutView(View):

    def get(self, request):
        user = request.user
        context = {
            'server_version': settings_local.VERSION,
            'user': user

        }

        return render(request, 'about.html', context)
