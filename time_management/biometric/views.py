from rest_framework.viewsets import ModelViewSet
from ..models import BiometricData
from time_management.biometric.serializers import BiometricDataSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def biometric_data_api(request, biometric_id=None):
    if request.method == "GET":
        if biometric_id:
            try:
                obj = BiometricData.objects.get(biometric_id=biometric_id)
                serializer = BiometricDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = BiometricData.objects.all()
            serializer = BiometricDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = BiometricDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BiometricDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
            obj.delete()
            return Response(
                {"message": "Biometric record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
