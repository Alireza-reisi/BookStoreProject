from django.urls import path
from .views import AuthorDetailView, ReactToCommentView, AuthorListView, BookDetailView

app_name = 'bookmanager'

urlpatterns = [
    path("react/<int:comment_id>/<str:reaction_type>/", ReactToCommentView, name="react_comment"),
    path("<slug:slug>/", BookDetailView.as_view(), name="book_detail"),
    path('author/<slug:slug>/', AuthorDetailView.as_view(), name='author_detail'),
    path("authors/", AuthorListView.as_view(), name="author_list"),
]
