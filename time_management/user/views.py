from rest_framework.viewsets import ModelViewSet
from ..models import User, PasswordResetOTP
from time_management.user.serializers import UserSerializer, UserDetailsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password

import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def user_api(request, user_id=None):
    if request.method == "GET":
        if user_id:
            try:
                user = User.objects.get(user_id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": f"User created with role {serializer.validated_data.get('role')}",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not user_id:
            return Response(
                {"error": "User ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(
            user, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not user_id:
            return Response(
                {"error": "User ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(user_id=user_id)
            user.delete()
            return Response(
                {"message": "User deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
def user_details(request, user_id=None):
    if user_id:
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserDetailsSerializer(user)
        return Response(serializer.data)
    else:
        users = User.objects.all()
        serializer = UserDetailsSerializer(users, many=True)
        return Response(serializer.data)


# @api_view(["GET"])
# def login_details(request, email=None, password=None):
#     if email:
#         if password:
#             try:
#                 user = User.objects.get(email=email)
#                 if check_password(password, user.password):
#                     auth_user = user
#                     serializer = UserDetailsSerializer(auth_user)
#                     return Response(serializer.data)
#                 else:
#                     return Response({"error": "Password is incorrect"})
#             except User.DoesNotExist:
#                 return Response({"error": "User not found"})
#         else:
#             return Response({"error": "Please provide password"})
#     else:
#         return Response({"error": "Please provide user and password"})


@api_view(["POST"])
def login_details(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Please provide user and password"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not check_password(password, user.password):
        return Response({"error": "Password is incorrect"}, status=400)

    serializer = UserDetailsSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
def send_reset_otp(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=400)
    try:
        user = User.objects.get(email=email)

        #  Check for recent OTP within last 60 seconds

        recent_otp = (
            PasswordResetOTP.objects.filter(
                user=user, created_at__gte=timezone.now() - timedelta(seconds=60)
            )
            .order_by("-created_at")
            .first()
        )

        if recent_otp:
            return Response(
                {"error": "You can request a new OTP only once every 60 seconds."},
                status=429,
            )
        # Invalidate any previous unused OTPs for this user:
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)

        try:
            send_mail(
                subject="Your OTP for Password Reset",
                message=f"Use this OTP to reset your password: \n\n{otp}\n\nThis OTP is valid for 10 minutes.\nRegards, \nAdmin team.",
                from_email=settings.DEFAULT_FROM_EMAIL,  #  use setting
                recipient_list=[email],
                fail_silently=False,
            )
            print("OTP sent to your mail")
            return Response({"message": "OTP sent to your email."}, status=200)

        except Exception as e:
            print("OTP send failed!!!!!!!")
            return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=404)


@api_view(["POST"])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).last()

        if not otp_obj:
            return Response({"error": "Invalid OTP."}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired."}, status=400)

        #  Securely hash the new password
        user.password = make_password(new_password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return Response({"message": "Password reset successful."}, status=200)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=404)
