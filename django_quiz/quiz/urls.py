try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from .views import QuizListView, CategoriesListView, \
    ViewQuizListByCategory, QuizUserProgressView, QuizMarkingList, \
    QuizMarkingDetail, QuizDetailView, QuizTake, QuizViewApi

from django_quiz.multichoice.views import MultichoiceAnswer,MultichoiceQuestion
from django_quiz.essay.views import EssayQuestion
from django_quiz.true_false.views import TFQuestion

urlpatterns = [

    url(r'^MCQuestion/$',
        view=MultichoiceQuestion.as_view(),
        name='MCQ_quiz'),

    url(r'^MCAnswer/$',
        view=MultichoiceAnswer.as_view(),
        name='MCQ_Answer_quiz'),

    url(r'^EssayQuestion/$',
        view=EssayQuestion.as_view(),
        name='Essay_quiz'),

    url(r'^TFQuestion/$',
        view=TFQuestion.as_view(),
        name='TF_quiz'),

    url(r'^Quiz/$',
        view=QuizViewApi.as_view(),
        name='quiz'),

    url(r'^$',
        view=QuizListView.as_view(),
        name='quiz_index'),

    url(r'^category/$',
        view=CategoriesListView.as_view(),
        name='quiz_category_list_all'),

    url(r'^category/(?P<category_name>[\w|\W-]+)/$',
        view=ViewQuizListByCategory.as_view(),
        name='quiz_category_list_matching'),

    url(r'^progress/$',
        view=QuizUserProgressView.as_view(),
        name='quiz_progress'),

    url(r'^marking/$',
        view=QuizMarkingList.as_view(),
        name='quiz_marking'),

    url(r'^marking/(?P<pk>[\d.]+)/$',
        view=QuizMarkingDetail.as_view(),
        name='quiz_marking_detail'),

    #  passes variable 'quiz_name' to quiz_take view
    url(r'^(?P<slug>[\w-]+)/$',
        view=QuizDetailView.as_view(),
        name='quiz_start_page'),

    url(r'^(?P<quiz_name>[\w-]+)/take/$',
        view=QuizTake.as_view(),
        name='quiz_question'),
]

