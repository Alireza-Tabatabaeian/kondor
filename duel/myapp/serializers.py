from .models import Course, Game, Question, UserProfile, DailyGame, GameRound
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class CourseRequestSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    course = serializers.IntegerField(min_value=1, required=True)
    game = serializers.IntegerField(min_value=1, required=True)


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class GameSerializerWithoutQuestions(serializers.ModelSerializer):
    class Meta:
        model = Game
        exclude = ['q1', 'q2', 'q3', 'q4', 'q5']


class DailyGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGame
        exclude = ['user']


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = '__all__'
