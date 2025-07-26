from drf_yasg import openapi

# Повторяющиеся схемы
PHONE_NUMBER_SCHEMA = openapi.Schema(
    type=openapi.TYPE_STRING,
    description="A phone number containing from 5 to 14 digits and may have a '+' before the number",
    example="+777777722"
)

CODE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_STRING,
    description="The four-digit authorization code that was sent to the phone number",
    example="4985"
)

INVITE_CODE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_STRING,
    description="A six-digit code of symbols and numbers generated during the user's first authorization",
    example="4uag2B"
)

ACTIVATED_CODE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_STRING,
    description="A six-digit referral code that can only be activated once",
    example="BWug2B"
)

REFERRALS_SCHEMA = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Schema(type=openapi.TYPE_STRING),
    example=["+7222142", "89223432"]
)

# Request bodies
AUTH_CODE_REQUEST_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["phone_number"],
    properties={
        "phone_number": PHONE_NUMBER_SCHEMA,
    },
)

CONFIRM_CODE_REQUEST_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "phone_number": PHONE_NUMBER_SCHEMA,
        "code": CODE_SCHEMA,
    }
)

ADD_REFERRAL_REQUEST_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="A six-digit code that can only be activated once",
    properties={
        "activated_code": ACTIVATED_CODE_SCHEMA
    }
)

# Response schemas
CODE_CREATED_RESPONSE = openapi.Response(
    description="Code created and sent to phone number",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, example="Code is created and sent to +777777722"),
            "code": openapi.Schema(type=openapi.TYPE_STRING, example="4985"),
        }
    )
)

USER_AUTHENTICATED_RESPONSE = openapi.Response(
    description="Successful authorization",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, example="User authenticated"),
            "new_user": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    )
)

USER_PROFILE_RESPONSE_SCHEMA = openapi.Response(
    description="User profile",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "phone_number": PHONE_NUMBER_SCHEMA,
            "invite_code": INVITE_CODE_SCHEMA,
            "activated_code": ACTIVATED_CODE_SCHEMA,
            "referrals": REFERRALS_SCHEMA,
        }
    )
)

ALL_USERS_RESPONSE_SCHEMA = openapi.Response(
    description="All user profiles",
    schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone_number": PHONE_NUMBER_SCHEMA,
                "invite_code": INVITE_CODE_SCHEMA,
                "activated_code": ACTIVATED_CODE_SCHEMA,
                "referrals": REFERRALS_SCHEMA,
            }
        )
    )
)

REFERRAL_ADDED_RESPONSE = openapi.Response(
    description="Referral code successfully added",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, example="Referral code successfully added"),
        }
    )
)

USER_DELETED_RESPONSE = openapi.Response(
    description="User deleted",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, example="User deleted"),
        }
    )
)
