from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.views import generic

from braces.views import SelectRelatedMixin

from groups.models import Group
from . import models, forms

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserM

from .models import Post

User = get_user_model()


class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ("user", "group")


class UserPosts(generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(
                username__iexact=self.kwargs.get('username')
            )
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super(UserPosts, self).get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ("user", "group")

    def get_queryset(self):
        queryset = super(PostDetail, self).get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))


@login_required()
def create_post(request, slug):
    print(slug)
    form = forms.PostForm()
    if request.method == "POST":
        form = forms.PostForm(request.POST)
        if form.is_valid():
            message = request.POST['message']
            group = Group.objects.get(slug=slug)
            user = UserM.objects.get(username=request.user.username)
            new_post = Post.objects.create(user=user, message=message, group=group)
            new_post.save()
            return redirect('posts:single', user.username, new_post.pk)
    return render(request, 'posts/post_form.html', {"form": form, 'slug': slug})


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ("user", "group")
    success_url = reverse_lazy("posts:all")

    def get_queryset(self):
        queryset = super(DeletePost, self).get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Post deleted")
        return super(DeletePost, self).delete()
