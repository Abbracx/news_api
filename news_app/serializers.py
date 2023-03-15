from rest_framework import serializers
from .models import HackerNews, User


class ReadUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username', 'email')
        read_only_fields = fields

class WriteUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class WriteHackerNewsSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    class Meta:
        model = HackerNews
        fields = ('by', 'descendants', 'kids',
                  'score', 'time', 'title', 'type', 'url', 'owner')
    


class ReadHackerNewsSerializer(serializers.ModelSerializer):
    owner = ReadUserSerializer()

    class Meta:
        model = HackerNews
        fields = (

            'news_id', 
            'by', 
            'descendants', 
            'kids', 
            'score', 
            'time', 
            'title', 
            'type', 
            'url', 
            'owner')
        read_only_fields = fields
