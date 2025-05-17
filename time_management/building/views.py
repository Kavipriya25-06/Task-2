from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from ..models import Building, BuildingAssign, ProjectAssign
from time_management.building.serializers import (
    BuildingSerializer,
    BuildingAssignSerializer,
    BuildingAndAssignSerializer,
    BuildingAndProjectSerializer,
)
from time_management.project.serializers import BuildingAssignFullSerializer


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


@api_view(["PATCH"])
def building_assign_update(request):
    updates = request.data  # list of dicts

    if not isinstance(updates, list):
        return Response({"error": "Expected a list of updates"}, status=400)

    updated = []
    received_ids = []
    project_assign_id = request.query_params.get("project_assign_id")

    if not project_assign_id:
        return Response({"error": "project_assign_id required"}, status=400)

    try:
        project_assign = ProjectAssign.objects.get(project_assign_id=project_assign_id)
    except ProjectAssign.DoesNotExist:
        return Response({"error": "Project assign not found"}, status=404)

    for item in updates:
        building_assign_id = item.get("building_assign_id", None)
        building_id = item.get("building_id")
        building_hours = item.get("building_hours", 0)
        status_update = item.get("status", "pending")

        if building_assign_id:
            # Update existing
            try:
                assign = BuildingAssign.objects.get(
                    building_assign_id=building_assign_id
                )
                assign.building_hours = building_hours
                assign.status = status_update
                assign.save()
                updated.append(building_assign_id)
                received_ids.append(building_assign_id)
            except BuildingAssign.DoesNotExist:
                continue
        else:
            # Create new
            new_assign = BuildingAssign.objects.create(
                project_assign=project_assign,
                building_id=building_id,
                building_hours=building_hours,
                status=status_update,
            )
            updated.append(new_assign.building_assign_id)
            received_ids.append(new_assign.building_assign_id)

    # Delete removed assignments:
    existing_assigns = BuildingAssign.objects.filter(project_assign=project_assign)
    for assign in existing_assigns:
        if assign.building_assign_id not in received_ids:
            assign.delete()

    return Response(
        {"message": "Buildings updated", "processed_ids": updated}, status=200
    )


@api_view(["GET"])
def building_and_assign(request, building_assign_id=None):
    if building_assign_id:
        try:
            buildings = BuildingAssign.objects.get(
                building_assign_id=building_assign_id
            )
        except BuildingAssign.DoesNotExist:
            return Response(
                {"error": "building not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = BuildingAndAssignSerializer(buildings)
        return Response(serializer.data)
    else:
        buildings = BuildingAssign.objects.all()
        serializer = BuildingAndAssignSerializer(buildings, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def building_and_project(request, building_assign_id=None):
    if building_assign_id:
        try:
            buildings = BuildingAssign.objects.get(
                building_assign_id=building_assign_id
            )
        except BuildingAssign.DoesNotExist:
            return Response(
                {"error": "building not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = BuildingAndProjectSerializer(buildings)
        return Response(serializer.data)
    else:
        buildings = BuildingAssign.objects.all()
        serializer = BuildingAndProjectSerializer(buildings, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def full_building_view(request, building_assign_id=None):
    if building_assign_id:
        try:
            project = BuildingAssign.objects.get(building_assign_id=building_assign_id)
        except BuildingAssign.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {"error": "building id not given"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = BuildingAssignFullSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@transaction.atomic
def create_building_with_assignment(request):
    try:
        # 1. Create Building
        building_data = request.data.get("building")
        if not building_data:
            return Response({"error": "Missing building data"}, status=400)

        building_serializer = BuildingSerializer(data=building_data)
        if building_serializer.is_valid():
            building_instance = building_serializer.save()
        else:
            return Response(
                {
                    "error": "Building creation failed",
                    "details": building_serializer.errors,
                },
                status=400,
            )

        # 2. Create BuildingAssign
        assign_data = request.data.get("assign")
        if not assign_data:
            return Response({"error": "Missing assignment data"}, status=400)

        assign_serializer = BuildingAssignSerializer(
            data={
                "building_hours": assign_data.get("building_hours"),
                "status": assign_data.get("status", "pending"),
                "employee": assign_data.get("employee"),
                "project_assign": assign_data.get("project_assign"),
                "building": building_instance.building_id,
            }
        )

        if assign_serializer.is_valid():
            assign_instance = assign_serializer.save()
        else:
            return Response(
                {
                    "error": "Building assignment failed",
                    "details": assign_serializer.errors,
                },
                status=400,
            )

        return Response(
            {
                "message": "Building and assignment created successfully.",
                "building_id": building_instance.building_id,
                "building_assign_id": assign_instance.building_assign_id,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#####
#####
#####
# old code

# @api_view(["PATCH"])
# def building_assign_update(request, building_assign_id):
#     try:
#         building_assign = BuildingAssign.objects.get(
#             building_assign_id=building_assign_id
#         )
#     except BuildingAssign.DoesNotExist:
#         return Response({"error": "Building assignment not found"}, status=404)

#     employees = request.data.get("employee", None)
#     building_hours = request.data.get("building_hours", None)
#     status_update = request.data.get("status", None)

#     # Update employees if provided
#     if employees is not None:
#         building_assign.employee.set(employees)

#     # Update building hours
#     if building_hours is not None:
#         building_assign.building_hours = building_hours

#     # Update status
#     if status_update is not None:
#         building_assign.status = status_update

#     building_assign.save()

#     return Response({"message": "Building assignment updated."}, status=200)


# @api_view(["PATCH"])
# def building_assign_update(request):
#     updates = request.data  # Expecting a list of dicts

#     if not isinstance(updates, list):
#         return Response({"error": "Expected a list of updates"}, status=400)

#     updated = []

#     for item in updates:
#         building_assign_id = item.get("building_assign_id")
#         building_hours = item.get("building_hours")

#         if not building_assign_id:
#             continue  # Skip invalid

#         try:
#             assign = BuildingAssign.objects.get(building_assign_id=building_assign_id)

#             if building_hours is not None:
#                 assign.building_hours = building_hours

#             # Optional: If you want to update status or employees
#             status_update = item.get("status", None)
#             if status_update:
#                 assign.status = status_update

#             employee_list = item.get("employee", None)
#             if employee_list is not None:
#                 assign.employee.set(employee_list)

#             assign.save()
#             updated.append(building_assign_id)

#         except BuildingAssign.DoesNotExist:
#             continue  # Skip if not found

#     return Response(
#         {"message": "Updated buildings", "updated_ids": updated}, status=200
#     )
