from django.urls import path
from .views import AuthorDetailView, ReactToCommentView

app_name = 'bookmanager'

urlpatterns = [
    path("react/<int:comment_id>/<str:reaction_type>/", ReactToCommentView, name="react_comment"),
    path('author/<slug:slug>/', AuthorDetailView.as_view(), name='author_detail'),
]
