from rest_framework import serializers


class InputSerializer(serializers.Serializer):
    message = serializers.CharField()
    weight = serializers.FloatField()
    height = serializers.FloatField()
    bmi = serializers.FloatField()
    exams_data = serializers.ListField(child=serializers.DictField(), required=False)
    appointments_data = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    messages = serializers.ListField(child=serializers.DictField(), required=False)
    gender = serializers.CharField()
    meds_data = serializers.ListField(child=serializers.DictField(), required=False)
    birthday = serializers.CharField()
