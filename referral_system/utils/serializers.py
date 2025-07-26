from rest_framework import serializers
import re

class PhoneNumberSerializerMixin:
    def validate_phone_number(self, value):
        if not re.match(r'^\+?\d{5,14}$', value):
            raise serializers.ValidationError("Invalid phone number")
        return value