from rest_framework import serializers

from management.models import TermsAndConditions


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['terms']
        extra_kwargs = {'terms': {'read_only': True}}
