
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .forms import CommentForm, UploadedFileForm
from .models import Choice, Comment, Question, UploadedFile


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

    return render(
        request,
        "polls/detail.html",
        {
            "question": question,
            "comments": question.comments.select_related("owner").all(),
        },
    )


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()

    total_votes = sum(choice.votes for choice in choices)

    return render(
        request,
        "polls/results.html",
        {
            "question": question,
            "choices": choices,
            "total_votes": total_votes,
        },
    )


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


@login_required
def add_comment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.question = question
            comment.owner = request.user
            comment.save()

            return HttpResponseRedirect(
                reverse("polls:detail", args=(question.id,))
            )
    else:
        form = CommentForm()

    return render(
        request,
        "polls/add_comment.html",
        {
            "question": question,
            "form": form,
        },
    )


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        owner=request.user,
    )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse("polls:detail", args=(comment.question.id,))
            )
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "polls/edit_comment.html",
        {
            "comment": comment,
            "question": comment.question,
            "form": form,
        },
    )


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        owner=request.user,
    )

    question_id = comment.question.id

    if request.method == "POST":
        comment.delete()

        return HttpResponseRedirect(
            reverse("polls:detail", args=(question_id,))
        )

    return render(
        request,
        "polls/delete_comment.html",
        {
            "comment": comment,
            "question": comment.question,
        },
    )


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.uploader = request.user
            uploaded_file.save()

            return HttpResponseRedirect(
                reverse("polls:upload_file")
            )
    else:
        form = UploadedFileForm()

    user_files = UploadedFile.objects.filter(
        uploader=request.user
    ).order_by("-uploaded_at")

    return render(
        request,
        "polls/upload.html",
        {
            "form": form,
            "user_files": user_files,
        },
    )


def weather(request):
    url = "https://api.weather.gov/gridpoints/OAX/83,60/forecast"

    weather_data = None
    error_message = None

    api_request = Request(
        url,
        headers={
            "User-Agent": "DjangoPollsExercise8 (student project)",
            "Accept": "application/geo+json",
        },
    )

    try:
        with urlopen(api_request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        periods = data["properties"]["periods"]
        weather_data = periods[:5]

    except (
        URLError,
        HTTPError,
        TimeoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ):
        error_message = (
            "Weather information is currently unavailable. "
            "Please try again later."
        )

    return render(
        request,
        "polls/weather.html",
        {
            "weather_data": weather_data,
            "error_message": error_message,
        },
    )
