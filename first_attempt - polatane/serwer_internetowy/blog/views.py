from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from django.http import HttpResponse
from django.db import connection


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    id = request.GET.get('id', '')
    return render(request, 'blog/about.html', {'id': id})


def search(request):
    #new" UNION SELECT email FROM auth_user;--
    if request.method == "POST":
        L = []
        get_text = request.POST.get("textfield", None)

        import re
        black_list = re.compile('[@_!#$%^&*()-+<>?/\|}{~:]')
        if (black_list.search(get_text) == None):
            cursor = connection.cursor()
            cursor.execute('''SELECT username FROM auth_user WHERE username LIKE "{}%"'''.format(get_text))
            temp = cursor.fetchone()

            while temp is not None:
                print(temp)
                L.append(str(temp) + "<br><br>")
                temp = cursor.fetchone()
            return HttpResponse(i for i in L)
        else:
            return render(request, 'blog/search.html')

    context= {}
    return render(request, 'blog/search.html', context)

def info(request):
    return render(request, 'blog/info.html')


