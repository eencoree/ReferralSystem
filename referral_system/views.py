import time
from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from drf_yasg import openapi
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ReferralSystem.settings import BASE_URL
from referral_system.models import User, UserPhoneCode
from referral_system.serializers import UserSerializer, UserPhoneCodeSerializer, UserProfileSerializer, \
    AddReferralSerializer
from .swagger_schemas import (
    AUTH_CODE_REQUEST_BODY, CODE_CREATED_RESPONSE,
    CONFIRM_CODE_REQUEST_BODY, USER_AUTHENTICATED_RESPONSE,
    USER_PROFILE_RESPONSE_SCHEMA, ALL_USERS_RESPONSE_SCHEMA,
    ADD_REFERRAL_REQUEST_BODY, REFERRAL_ADDED_RESPONSE,
    USER_DELETED_RESPONSE,
)


class RequestCode(APIView):
    authentication_classes = ()

    @swagger_auto_schema(
        operation_description="Get an authorization code by phone number",
        tags=["Authorization code"],
        request_body=AUTH_CODE_REQUEST_BODY,
        responses={
            201: CODE_CREATED_RESPONSE,
            400: openapi.Response(description="Bad request"),
        }
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'message': 'phone_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(phone_number=phone_number).exists():
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']

        user_phone_code = UserPhoneCode.objects.filter(phone_number=phone_number).first()
        if user_phone_code:
            if timezone.now() < user_phone_code.created_at + timedelta(seconds=30):
                return Response({'message': 'The authentication code was requested less than 30 seconds ago'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                user_phone_code.code = user_phone_code.generate_4xcode()
                auth_code = user_phone_code.code
                user_phone_code.save()
        else:
            auth_code = UserPhoneCode.generate_4xcode()
            UserPhoneCode.objects.create(phone_number=phone_number, code=auth_code)
        time.sleep(1)
        return Response({"message": f"Code is created and sent to {phone_number}",
                         "code": auth_code}, status=status.HTTP_201_CREATED)


class ConfirmCode(APIView):
    authentication_classes = ()

    @swagger_auto_schema(
        operation_description="Confirmation of the authorization code",
        tags=["Confirmation"],
        request_body=CONFIRM_CODE_REQUEST_BODY,
        responses={
            200: USER_AUTHENTICATED_RESPONSE,
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found"),
        }
    )
    def post(self, request):
        created = False
        serializer = UserPhoneCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        auth_code = serializer.validated_data['code']

        try:
            code_obj = UserPhoneCode.objects.get(phone_number=phone_number)
        except UserPhoneCode.DoesNotExist:
            return Response({"message": f"Code not found"}, status=status.HTTP_404_NOT_FOUND)

        if code_obj.is_expired():
            return Response({"message": f"Code expired"}, status=status.HTTP_400_BAD_REQUEST)

        if code_obj.code != auth_code:
            return Response({"message": f"Code invalid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            user = User.objects.create_user(phone_number=phone_number)
            created = True
        login(request, user)
        code_obj.delete()
        return Response({"message": "User authenticated", "new_user": created}, status=status.HTTP_200_OK)


class UserProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Get user profile",
        tags=["UserProfile"],
        responses={
            200: USER_PROFILE_RESPONSE_SCHEMA
        }
    )
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class AllUsers(APIView):

    @swagger_auto_schema(
        operation_description="Get all user profiles",
        tags=["UserProfiles"],
        responses={
            200: ALL_USERS_RESPONSE_SCHEMA
        }
    )
    def get(self, request):
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


class AddReferral(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Add referral to user",
        tags=["Referral"],
        request_body=ADD_REFERRAL_REQUEST_BODY,
        responses={
            200: REFERRAL_ADDED_RESPONSE,
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found"),
        }
    )
    def patch(self, request):
        user = request.user
        serializer = AddReferralSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.activated_code:
            return Response({"message": "Referral code already activated"}, status=status.HTTP_400_BAD_REQUEST)
        activated_code = serializer.validated_data['activated_code']

        if User.objects.filter(Q(invite_code=activated_code) & ~Q(phone_number=user.phone_number)).exists():
            user.activated_code = activated_code
            user.save()
        else:
            return Response({"message": f"Referral code not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Referral code successfully added"}, status=status.HTTP_200_OK)


class DeleteUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Delete user",
        tags=["Delete"],
        responses={
            200: USER_DELETED_RESPONSE
        }
    )
    def delete(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        for referral in serializer.data['referrals']:
            referral_user = User.objects.get(phone_number=referral)
            referral_user.activated_code = None
            referral_user.save()
        UserPhoneCode.objects.get(phone_number=user.phone_number).delete()
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)


# ---------------- Test --------------------
class GetAuthCodeView(View):
    template_name = "request_code.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        try:
            api_response = requests.post(
                f"{BASE_URL}/referral/auth/",
                json={"phone_number": phone_number}
            )
            response_data = api_response.json()
        except Exception as e:
            response_data = {"error": str(e)}

        return render(request, self.template_name, {"response": response_data})


def confirm_code_logic(request, phone_number, code):
    try:
        code_obj = UserPhoneCode.objects.get(phone_number=phone_number)
    except UserPhoneCode.DoesNotExist:
        return {"status": 404, "message": "Code not found"}

    if code_obj.is_expired():
        return {"status": 400, "message": "Code expired"}

    if code_obj.code != code:
        return {"status": 400, "message": "Code invalid"}

    try:
        user = User.objects.get(phone_number=phone_number)
        created = False
    except User.DoesNotExist:
        user = User.objects.create_user(phone_number=phone_number)
        created = True

    login(request, user)
    code_obj.delete()

    return {"status": 200, "message": "User authenticated", "new_user": created}


class ConfirmCodeView(View):
    template_name = "confirm_code.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get('phone_number')
        code = request.POST.get('code')

        result = confirm_code_logic(request, phone, code)

        return render(request, self.template_name, {'response': result})


class GetProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        serializer = UserProfileSerializer(self.request.user)
        context['user_profile'] = serializer.data
        return context


class GetUserProfilesView(View):
    template_name = 'user_profiles.html'

    def get(self, request):
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return render(request, self.template_name, {'users': serializer.data})


class AddReferralView(LoginRequiredMixin, View):
    template_name = 'add_referral.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        activated_code = request.POST.get('activated_code', '').strip()
        context = {'activated_code': activated_code}

        if not activated_code:
            context['error'] = "Please enter a referral code"
            return render(request, self.template_name, context)

        user = request.user
        serializer = AddReferralSerializer(data={'activated_code': activated_code})
        if not serializer.is_valid():
            context['error'] = "Invalid code format"
            return render(request, self.template_name, context)

        if user.activated_code:
            context['error'] = "Referral code already activated"
            return render(request, self.template_name, context)

        if User.objects.filter(Q(invite_code=activated_code) & ~Q(phone_number=user.phone_number)).exists():
            user.activated_code = activated_code
            user.save()
            context['message'] = "Referral code successfully added"
        else:
            context['error'] = "Referral code not found"

        return render(request, self.template_name, context)


class DeleteUserView(LoginRequiredMixin, View):
    template_name = 'delete_user.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        for referral_phone in serializer.data.get('referrals', []):
            try:
                referral_user = User.objects.get(phone_number=referral_phone)
                referral_user.activated_code = None
                referral_user.save()
            except User.DoesNotExist:
                pass

        UserPhoneCode.objects.filter(phone_number=user.phone_number).delete()
        user.delete()
        return redirect('test_auth')
