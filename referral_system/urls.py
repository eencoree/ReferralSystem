from django.urls import path

from referral_system.views import RequestCode, ConfirmCode, UserProfile, AddReferral, AllUsers, DeleteUser, \
    GetAuthCodeView, ConfirmCodeView, GetProfileView, GetUserProfilesView, AddReferralView, DeleteUserView

urlpatterns = [
    path("auth/", RequestCode.as_view(), name="first_auth"),
    path("confirm/", ConfirmCode.as_view(), name="confirm_code"),
    path("users/", AllUsers.as_view(), name="all_users"),
    path("delete/", DeleteUser.as_view(), name="delete_user"),
    path("profile/", UserProfile.as_view(), name="profile"),
    path("code/", AddReferral.as_view(), name="referral"),

    # --------------- Test ----------------
    path("test/auth/", GetAuthCodeView.as_view(), name="test_auth"),
    path("test/confirm/", ConfirmCodeView.as_view(), name="test_confirm"),
    path("test/profile/", GetProfileView.as_view(), name="test_profile"),
    path("test/users/", GetUserProfilesView.as_view(), name="test_user_profiles"),
    path("test/code/", AddReferralView.as_view(), name="test_code"),
    path("test/delete/", DeleteUserView.as_view(), name="test_delete"),
]