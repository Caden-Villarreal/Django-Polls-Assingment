import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [],
        )

    def test_past_question(self):
        question = Question.objects.create(
            question_text="Past question.",
            pub_date=timezone.now() - datetime.timedelta(days=1),
        )
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        Question.objects.create(
            question_text="Future question.",
            pub_date=timezone.now() + datetime.timedelta(days=1),
        )
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [],
        )

    def test_future_question_and_past_question(self):
        question = Question.objects.create(
            question_text="Past question.",
            pub_date=timezone.now() - datetime.timedelta(days=1),
        )

        Question.objects.create(
            question_text="Future question.",
            pub_date=timezone.now() + datetime.timedelta(days=1),
        )

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )
    def test_two_past_questions(self):
        question1 = Question.objects.create(
            question_text="Past question 1.",
            pub_date=timezone.now() - datetime.timedelta(days=2),
        )

        question2 = Question.objects.create(
            question_text="Past question 2.",
            pub_date=timezone.now() - datetime.timedelta(days=1),
        )

        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = Question.objects.create(
            question_text="Future question.",
            pub_date=timezone.now() + datetime.timedelta(days=5),
        )

        response = self.client.get(
            reverse("polls:detail", args=(future_question.id,))
        )

        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = Question.objects.create(
            question_text="Past question.",
            pub_date=timezone.now() - datetime.timedelta(days=5),
        )

        response = self.client.get(
            reverse("polls:detail", args=(past_question.id,))
        )

        self.assertContains(response, past_question.question_text)