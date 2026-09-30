from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def index(request):
    latest_question_list = Question.objects.filter(
        pub_date__lte=timezone.now()
    ).order_by("-pub_date")[:5]

    if request.COOKIES.get("visited_polls"):
        welcome_message = "Welcome back to the Polls application."
    else:
        welcome_message = "Welcome to the Polls application."

    visit_count = request.session.get("visit_count", 0)
    visit_count += 1
    request.session["visit_count"] = visit_count
    request.session.save()

    last_poll = None
    last_poll_id = request.session.get("last_poll")

    if last_poll_id:
        try:
            last_poll = Question.objects.get(pk=last_poll_id)
        except Question.DoesNotExist:
            last_poll = None
            request.session.pop("last_poll", None)

    context = {
        "latest_question_list": latest_question_list,
        "welcome_message": welcome_message,
        "visit_count": visit_count,
        "last_poll": last_poll,
    }

    response = render(request, "polls/index.html", context)
    response.set_cookie("visited_polls", "yes", max_age=120)

    return response


def detail(request, question_id):
    question = get_object_or_404(
        Question.objects.filter(pub_date__lte=timezone.now()),
        pk=question_id,
    )

    request.session["last_poll"] = question.id
    request.session.save()

    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()

        return HttpResponseRedirect(
            reverse("polls:results", args=(question.id,))
        )