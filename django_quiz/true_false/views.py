from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers
from teachers import models as teachers_models
from departments import serializers as departments_serializers
from departments import models as departments_models
from students import models as student_models
from sections import models as section_models
from students import serializers as student_serializers
from sections import serializers as section_serializers
from teachers import serializers as teachers_serializers
from users import models as users_models
from utils.decorators import is_organization, validate_org, validate_dept

# Utils
import json



#TODO:figure not working
class TFQuestion(views.APIView):

    serializer_class = serializers.TFQuestionSerializer
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)


    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "true_false question",
            type=openapi.TYPE_OBJECT,
            properties={
                'question': openapi.Schema(type=openapi.TYPE_STRING),
                'explanation': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER),
                'sub-category': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quiz': openapi.Schema(type=openapi.TYPE_INTEGER),
                'correct': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    def post(self, request):
        data = request.data
        quiz = data.get('quiz')
        category = data.get('category')
        sub_category = data.get('sub_category',"")
        figure = data.get('figure',"")
        question = data.get('question',"")
        explanation = data.get('explanation',"")
        correct = data.get('correct',"")

        data_dict= {
            "content": question,
            "quiz": [quiz],
            "category": category,
            "sub_category": sub_category,
            # "figure": figure,
            "explanation": explanation,
            "correct": correct,
        }
        serializer = self.serializer_class(data=data_dict)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response({'details':serializer.errors}, status.HTTP_400_BAD_REQUEST)

# Token a2850ba0f2646f192af7111841ea958d767a0789 : User - Prashant
