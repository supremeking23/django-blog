from django.shortcuts import render, get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm,CommentForm, SearchForm

def post_search(request):
	form = SearchForm()
	query = None
	results = []
	if 'query' in request.GET:
		form = SearchForm(request.GET)
		if form.is_valid():
			query = form.cleaned_data['query']
			#search_vector = SearchVector('title', 'body')
			search_vector = SearchVector('title',weight='A') + SearchVector('body', weight='B')
			search_query = SearchQuery(query)
			results = Post.objects.annotate(
					search=search_vector,
					rank = SearchRank(search_vector, search_query)
				).filter(rank__gte=0.3).order_by('-rank')
			#.filter(search=search_query).order_by('-rank')
			#results = Post.objects.annotate(search=SearchVector('title','body'),).filter(search=query)
			#results	=Post.objects.annotate(search=SearchVector('title',	'body'),).filter(search=query)		
	return render(request,'blogs/post/search.html',{'form':form,'query':query,'results':results})




def post_share(request, post_id):
	# retrieve post by id
	post = get_object_or_404(Post,id=post_id,status='published')
	sent = False

	if request.method == 'POST':
		# form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# Form fields passed validation
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = '{} ({}) recommends your reading "{}"'.format(cd['name'],cd['email'],post.title)
			message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,post_url,cd['name'],cd['comments'])
			send_mail(subject, message, 'icjfuncion@gmail.com',[cd['to']],fail_silently=False)

			#testing
			# subject = 'Testing'
			# message = 'Testing body'
			# email_from = settings.EMAIL_HOST_USER
			# recipient_list = ['icjfuncion@gmail.com',]
			# send_mail(subject,message,email_from,recipient_list)
			sent =True
	else:
		form = EmailPostForm()

	
	return render(request,'blogs/post/share.html',{'post':post,'form':form,'sent':sent})


# class PostListView(ListView):
# 	queryset = Post.published.all()
# 	context_object_name = 'posts'
# 	paginate_by = 3
# 	template_name = 'blogs/post/list.html'

def post_list(request, tag_slug=None):
	object_list = Post.published.all()
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])


	paginator = Paginator(object_list, 3) #  posts in each page
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer deliver the first page
		posts = paginator.page(1)
	except EmptyPage:
		#if page is out of range deliver last page of results
		posts = paginator.page(paginator.num_pages)



	return render(request,'blogs/post/list.html',{'page':page,'posts':posts,'tag':tag})
# 	# posts = Post.published.all()
# 	# return render(request,'blogs/post/list.html',{'posts':posts})

def post_detail(request,year,month,day,post):
	post = get_object_or_404(Post, slug=post,status='published',publish__year=year,publish__month=month,publish__day=day)

	# List of active comments for this post
	comments = post.comments.filter(active=True)

	#initalize
	new_comment = None

	if request.method == 'POST':
		# a comment was posted
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			# Create comment object but don't save to database yet
			new_comment = comment_form.save(commit=False)
			# Assign the current post to the comment
			new_comment.post = post
			# Save the comment to the database
			new_comment.save()

	else:
		comment_form = CommentForm()


	# List of similar posts

	post_tags_ids = post.tags.values_list('id',flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids)\
								  .exclude(id=post.id)

	similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
							     .order_by('-same_tags','-publish')[:4]

	return render(request,'blogs/post/detail.html',{'post':post,'comments':comments,'comment_form':comment_form,'new_comment':new_comment,'similar_posts':similar_posts})


# # Create your views here.

# # filters in django
# # Post.objects.filter(publish__year=2015)
# # multiple filter filter by year published and the author
# # Post.objects.filter(publish__year=2017,author='ivan')
# # same as above but in chain 
# # Post.objects.filter(publish__year=2017) \
# # 			.filter(auther__username='admin')

# # publish__year and author__username are field lookups

# # Using exclude() # all but except for the this one
# # # get all post in 2017 excluding the title that starts with
# # Post.objects.filter(publish__year=2017) \
# # 			.exclude(title_startswith='why')

# # Using order_by()
# # Post.object.order_by('title')
# # # by default, it is in ascending order
# # #you can change it to descending order by putting a negative sign prefix
# # Post.object.order_by('-title')

# Deleting objects
# post = Post.objects.get(id=1)
# post.delete()
# # if you delete an object it will also delete any dependent relationships for foreignkey
