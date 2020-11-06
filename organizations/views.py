from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q
from . import models
from departments import models as departments_models
from departments import serializers as departments_serializers

# Utils
import json

class JoinRequests(views.APIView):

    queryset = models.Organization.objects.filter(is_active=True)

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        org_id = request.data.get('org_id')

        if not org_id:
            errors = [
                'org_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            
        organizations = self.queryset.filter(Q(user__id=request.user.id) & Q(org_id=org_id))

        if not len(organizations):
            errors = [
                'Invalid org_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = departments_models.Department.objects.filter(Q(requested_organization__id=organizations[0].id) & Q(is_active=True))

        serializer = departments_serializers.DepartmentSerializer(departments, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(json.dumps(request.data))
        org_id = data.get('org_id')
        departments = str(data.get("departments", "[]"))


        if not org_id:
            errors = [
                'org_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            
        organizations = self.queryset.filter(Q(user__id=request.user.id) & Q(org_id=org_id))

        if not len(organizations):
            errors = [
                'Invalid org_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        # issue department is not working
        if not departments:
            errors = [
                'departments not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        try:
            departments = departments.replace(" ", "")
            departments = departments[1:len(departments)-1].split(",")
            departments = [int(i) for i in departments]
        except Exception as e:
            errors = [
                "departments format should be like this. [1, 2, 3] where 1, 2 and 3 are department ID's",
                str(e)
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        dept_qs = departments_models.Department.objects.filter(is_active=True)


        valid_departments = []

        for i in departments:
            temp_depts = dept_qs.filter(id=i)
            if not len(temp_depts):
                errors = [
                    'Invalid department ID'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            temp_dept = temp_depts[0]
            if not temp_dept.requested_organization or temp_dept.requested_organization.user.id != request.user.id:
                errors = [
                    'Invalid department ID'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            valid_departments.append(temp_dept)

        for temp_dept in valid_departments:
            temp_dept.organization = temp_dept.requested_organization
            temp_dept.requested_organization = None
            temp_dept.save()

        return Response({"details": ["Successfully accepted all provided requests."]}, status.HTTP_200_OK)
