from .utils.serializers import PhoneNumberSerializerMixin

from django.db.models import Q
from rest_framework import serializers

from referral_system.models import User, UserPhoneCode


class UserSerializer(serializers.ModelSerializer, PhoneNumberSerializerMixin):
    phone_number = serializers.CharField(
        help_text="A phone number containing from 5 to 14 digits and may have a '+' before the number\n"
                  "example='+777777722'"
    )

    class Meta:
        model = User
        fields = ("phone_number",)


class UserPhoneCodeSerializer(serializers.ModelSerializer, PhoneNumberSerializerMixin):
    phone_number = serializers.CharField(
        help_text="A phone number containing from 5 to 14 digits and may have a '+' before the number\n"
                  "example='+777777722'",
    )
    code = serializers.CharField(
        help_text="The four-digit authorization code that was sent to the phone number\n"
                  "example='4985'"
    )

    class Meta:
        model = UserPhoneCode
        fields = ("phone_number", "code",)


class UserProfileSerializer(serializers.ModelSerializer, PhoneNumberSerializerMixin):
    phone_number = serializers.CharField(
        help_text="A phone number containing from 5 to 14 digits and may have a '+' before the number\n"
                  "example='+777777722'",
    )
    invite_code = serializers.CharField(
        help_text="A six-digit code of symbols and numbers generated during the user's first authorization\n"
                  "example='4uag2B'"
    )
    activated_code = serializers.CharField(
        help_text="A six-digit referral code that can only be activated once\n"
                  "example='BWug2B'"
    )
    referrals = serializers.SerializerMethodField(
        help_text="The list of referrals that have activated the user's invite_code\n"
                  "example='['+7222142', '89223432']'"
    )

    class Meta:
        model = User
        fields = ("phone_number", "invite_code", "activated_code", "referrals")

    def get_referrals(self, obj):
        users = User.objects.filter(Q(activated_code=obj.invite_code) & ~Q(phone_number=obj.phone_number))
        return [user.phone_number for user in users]


class AddReferralSerializer(serializers.ModelSerializer):
    activated_code = serializers.CharField(
        help_text="A six-digit code that can only be activated once\n"
                  "example='BWug2B'",
    )

    class Meta:
        model = User
        fields = ("activated_code",)
