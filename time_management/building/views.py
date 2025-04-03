from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import Building, BuildingAssign
from time_management.building.serializers import (
    BuildingSerializer,
    BuildingAssignSerializer,
)


@api_view(["GET", "POST"])
def building_list_create(request):
    if request.method == "GET":
        buildings = Building.objects.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Building created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def building_detail(request, building_id):
    try:
        building = Building.objects.get(building_id=building_id)
    except Building.DoesNotExist:
        return Response(
            {"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = BuildingSerializer(building)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = BuildingSerializer(building, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Building updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        building.delete()
        return Response(
            {"message": "Building deleted"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET", "POST"])
def building_assign_list_create(request):
    if request.method == "GET":
        buildings = BuildingAssign.objects.all()
        serializer = BuildingAssignSerializer(buildings, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = BuildingAssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Building assigned", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def building_assign_detail(request, building_assign_id):
    try:
        building = BuildingAssign.objects.get(building_assign_id=building_assign_id)
    except BuildingAssign.DoesNotExist:
        return Response(
            {"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = BuildingAssignSerializer(building)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = BuildingAssignSerializer(
            building, data=request.data, partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Building assignment updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        building.delete()
        return Response(
            {"message": "Building deleted"}, status=status.HTTP_204_NO_CONTENT
        )
