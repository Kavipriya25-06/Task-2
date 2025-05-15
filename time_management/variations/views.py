from rest_framework.viewsets import ModelViewSet
from ..models import Variation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from time_management.variations.serializers import VariationSerializer


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def variation_api(request, id=None):
    if request.method == "GET":
        if id:
            try:
                variation = Variation.objects.get(id=id)
                serializer = VariationSerializer(variation)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Variation.DoesNotExist:
                return Response(
                    {"error": "Variation not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            variations = Variation.objects.all()
            serializer = VariationSerializer(variations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = VariationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": f"variation created ",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "User ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            variation = Variation.objects.get(id=id)
        except Variation.DoesNotExist:
            return Response(
                {"error": "variation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = VariationSerializer(
            variation, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "variation updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "variation ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            variation = Variation.objects.get(id=id)
            variation.delete()
            return Response(
                {"message": "User deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Variation.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
