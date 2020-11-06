from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from . import models, serializers
from organizations import models as organizations_models

# Utils
import json


class Department(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer

    def post(self, request):
        data = json.loads(json.dumps(request.data))
        org_join_id = data.get("org_join_id")

        if not org_join_id:
            errors = [
                'Org_Join_ID  is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organizations = organizations_models.Organization.objects.filter(join_id=org_join_id)
        if not len(organizations):
            errors = [
                'Invalid organization Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organization = organizations[0]

        if not organization.is_active:
            errors = [
                'Invalid organization Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not organization.accepting_req:
            errors = [
                'This organization is not accepting requests currently.'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        data.update({
            "user": request.user.id,
            "requested_organization": organization.id
        })

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
