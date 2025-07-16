from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["email"] = self.user.email
        data["role"] = self.user.role
        data["user_id"] = self.user.user_id
        data["employee_id"] = self.user.employee_id.employee_id
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
import logging


@csrf_exempt
def run_biometric_sync(request):
    if request.method == "POST":
        try:
            call_command(
                "sync_monthly_biometric"
            ) 
            return JsonResponse(
                {"status": "success", "message": "Biometric sync started."}
            )
        except Exception as e:
            logging.exception("Failed to run biometric sync command")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )
