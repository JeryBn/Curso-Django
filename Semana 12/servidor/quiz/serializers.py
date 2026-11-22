from django.db import transaction
from rest_framework import serializers

from .models import Choice, Exam, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "created_at", "question_count"]
        read_only_fields = ["created_at"]


class QuestionSerializer(serializers.ModelSerializer):
    # Choices travel nested inside the question; the exam travels as an identifier.
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "exam", "text", "choices", "created_at"]
        read_only_fields = ["created_at"]

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Una pregunta necesita al menos dos opciones.")
        if sum(1 for choice in value if choice.get("is_correct")) != 1:
            raise serializers.ValidationError("Debe haber exactamente una opción correcta.")
        return value

    def create(self, validated_data):
        choices = validated_data.pop("choices")
        with transaction.atomic():
            question = Question.objects.create(**validated_data)
            Choice.objects.bulk_create(Choice(question=question, **choice) for choice in choices)
        return question

    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if choices is not None:  # sent choices replace the old ones
                instance.choices.all().delete()
                Choice.objects.bulk_create(Choice(question=instance, **choice) for choice in choices)
        return instance


class ChoiceResourceSerializer(serializers.ModelSerializer):
    """Standalone choice writes preserve the question's answer invariant."""

    class Meta:
        model = Choice
        fields = ["id", "question", "text", "is_correct"]

    def validate_question(self, value):
        if self.instance and self.instance.question_id != value.pk:
            raise serializers.ValidationError(
                "No se puede trasladar una opción a otra pregunta."
            )
        return value

    def validate_parent(self, attributes):
        question = attributes.get("question")
        if question is None and self.instance:
            question = self.instance.question
        if question is None:
            return attributes
        others = Choice.objects.filter(question=question)
        if self.instance:
            others = others.exclude(pk=self.instance.pk)
        correct = attributes.get(
            "is_correct", self.instance.is_correct if self.instance else False
        )
        if others.count() + 1 < 2:
            raise serializers.ValidationError(
                "Una pregunta necesita al menos dos opciones."
            )
        if others.filter(is_correct=True).count() + int(correct) != 1:
            raise serializers.ValidationError(
                "Debe haber exactamente una opción correcta."
            )
        return attributes

    def validate(self, attributes):
        return self.validate_parent(attributes)

    @transaction.atomic
    def create(self, validated_data):
        Question.objects.select_for_update().get(pk=validated_data["question"].pk)
        self.validate_parent(validated_data)
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        Question.objects.select_for_update().get(pk=instance.question_id)
        self.validate_parent(validated_data)
        return super().update(instance, validated_data)
