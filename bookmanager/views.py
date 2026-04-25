from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book, Author, Publisher, Category

# class CategoryView(ListView):
#     model = Category
#     template_name = "bookmanager/category_list.html"
#     context_object_name = "categories"
#
#
# class BookListView(ListView):
#     model = Book
#     template_name = "bookmanager/book_list.html"
#     context_object_name = "books"
#     paginate_by = 12
#
#
# class BookDetailView(DetailView):
#     model = Book
#     template_name = "bookmanager/book_detail.html"
#     context_object_name = "book"
#
#
# class BookCreateView(CreateView):
#     model = Book
#     template_name = "bookmanager/book_form.html"
#     fields = "__all__"
#
#
# class BookUpdateView(UpdateView):
#     model = Book
#     template_name = "bookmanager/book_form.html"
#     fields = "__all__"
#
#
# class BookDeleteView(DeleteView):
#     model = Book
#     template_name = "bookmanager/book_confirm_delete.html"
#     success_url = "/books/"
#
#
# class AuthorView(ListView):
#     model = Author
#     template_name = "bookmanager/author_list.html"
#     context_object_name = "authors"
#
#
# class PublisherView(ListView):
#     model = Publisher
#     template_name = "bookmanager/publisher_list.html"
#     context_object_name = "publishers"
