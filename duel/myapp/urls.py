from django.urls import path
from .views import course_selection, send_answers, update_game, \
    daily_game_endpoint, update_user_questions, UserLogin, UserLoginVerify, UserSignUpRequest, UsernameAvailability, \
    UserSignUpFinal, FastUserSignup, GameRequest

urlpatterns = [
    # retrieves profile details of the currently logged in user
    # path("profile/<int:pk>", UserProfileDetailView.as_view(), name="profile"),

    path("mobile-login", UserLogin.as_view(), name="mobile login"),
    path("mobile-verify", UserLoginVerify.as_view(), name="mobile verify"),
    path("check-username/<str:username>", UsernameAvailability.as_view(), name="check-username"),
    path("signup", UserSignUpFinal.as_view(), name="signup"),
    path("signup-request", UserSignUpRequest.as_view(), name="signup-request"),
    path("fastsignup", FastUserSignup.as_view(), name="fast-signup"),
    path("test", update_game, name="test"),

    # This path is called for begging of a game
    path("game-request", GameRequest.as_view(), name="game-request"),
    # This path returns course info for game
    path("course-request/<int:game_id>", course_selection, name="course-selection"),
    # send answers for a game
    path("send-answer", send_answers, name="send-answer"),
    # get game updates path
    path("get-game-updates/<int:game_id>", update_game, name="get-update-without-hash"),
    path("get-game-updates/<int:game_id>/<str:hash>", update_game, name="get-update-with-hash"),
    path("daily-game", daily_game_endpoint, name="daily-game-endpoint"),

    path("update-questions/<int:id>", update_user_questions, name="update-users-question"),
]
