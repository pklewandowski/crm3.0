from rest_framework import serializers

from apps.report.models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        exclude = ('xml_data',)
