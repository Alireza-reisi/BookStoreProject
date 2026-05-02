from django.urls import path
from .views import AuthorDetailView, ReactToCommentView, AuthorListView, BookDetailView, BookListView, \
    PublisherListView, PublisherDetailView

app_name = "bookmanager"

urlpatterns = [
    path("react/<int:comment_id>/<str:reaction_type>/", ReactToCommentView, name="react_comment"),
    path("categories/", BookListView.as_view(), name="book_list"),
    path("book/<slug:slug>/", BookDetailView.as_view(), name="book_detail"),
    path("authors/", AuthorListView.as_view(), name="author_list"),
    path("author/<slug:slug>/", AuthorDetailView.as_view(), name="author_detail"),
    path("publishers/", PublisherListView.as_view(), name="publisher_list"),
    path('publisher/<slug:slug>/', PublisherDetailView.as_view(), name="publisher_detail"),
]
