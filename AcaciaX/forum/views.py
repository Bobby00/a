from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy, reverse

from .forms import NewTopicForm, PostForm

from analysis.models import AnalysisArticle
from SliderArticles.models import SliderArticle
from news.models import NewsArticle, NewsPost
from .models import Category, Topic, Post, Preference

class HomeListView(ListView):
    model = Post
    context_object_name = 'home_posts'
    template_name = 'index.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['news_lists'] = NewsArticle.objects.all()
        context['slider_lists'] = SliderArticle.objects.all()
        context['analysis_objects'] = AnalysisArticle.objects.all()
        return context    

def economic_calendar(request):
    return render(request, 'economic-calendar.html')

def market_screener(request):
    return render(request, 'market-screener.html')

def real_time_widget(request):
    return render(request, 'real-time-widget.html')

class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'forum.html'


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'forum-topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['category'] = self.category
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        queryset = self.category.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

# def category_topics(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     topics = category.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     return render(request, 'forum-topics.html', {'category': category, 'topics': topics})

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        context = super().get_context_data(**kwargs)
        context['analysis_objects'] = AnalysisArticle.objects.all()
        context['category_list'] = Category.objects.all()
        return context

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, category__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('-created_at')
        return queryset

# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, category__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic': topic})

@login_required
def new_topic(request, pk):
    category = get_object_or_404(Category, pk=pk)
    user = User.objects.first()  # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)  # TODO: redirect to the created topic page
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'category': category, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, category__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.category.pk, topic_pk=post.topic.pk)


@login_required
def postpreference(request, pk, topic_pk, post_pk, userpreference):
        
    if request.method == "POST":
            eachpost= get_object_or_404(Post, id=post_pk)
            obj=''
            valueobj=''
            try:
                obj= Preference.objects.get(user= request.user, post=eachpost)
                valueobj= obj.value #value of userpreference
                valueobj= int(valueobj)
                userpreference= int(userpreference)
        
                if valueobj != userpreference:

                        obj.delete()
                        upref= Preference()
                        upref.user= request.user
                        upref.post= eachpost
                        upref.value= userpreference

                        if userpreference == 1 and valueobj != 1:
                                eachpost.likes += 1
                                eachpost.dislikes -=1
                        elif userpreference == 2 and valueobj != 2:
                                eachpost.dislikes += 1
                                eachpost.likes -= 1
                        
                        upref.save()
                        eachpost.save()
                
                        context= {'eachpost': eachpost,
                          'post_pk': post_pk}

                        return render (request, 'topic_posts.html', context)

                elif valueobj == userpreference:
                        obj.delete()
                
                        if userpreference == 1:
                                eachpost.likes -= 1
                        elif userpreference == 2:
                                eachpost.dislikes -= 1

                        eachpost.save()

                        context= {'eachpost': eachpost,
                          'post_pk': post_pk}

                        return render (request, 'topic_posts.html', context)
                            
            except Preference.DoesNotExist:
                    upref= Preference()
                    upref.user= request.user
                    upref.post= eachpost
                    upref.value= userpreference
                    userpreference= int(userpreference)

                    if userpreference == 1:
                            eachpost.likes += 1
                    elif userpreference == 2:
                            eachpost.dislikes +=1

                    upref.save()
                    eachpost.save()                            
                    context= {'eachpost': eachpost,
                      'post_pk': post_pk}
                    return render (request, 'topic_posts.html', context)

    else:
        eachpost= get_object_or_404(Post, id=post_pk)
        context= {'eachpost': eachpost,
                  'post_pk': post_pk}
        return render (request, 'topic_posts.html', context)
