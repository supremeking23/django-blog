from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.views.generic import ListView


class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blogs/post/list.html'

# def post_list(request):
# 	object_list = Post.published.all()
# 	paginator = Paginator(object_list, 3) #  posts in each page
# 	page = request.GET.get('page')
# 	try:
# 		posts = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer deliver the first page
# 		posts = paginator.page(1)
# 	except EmptyPage:
# 		#if page is out of range deliver last page of results
# 		posts = paginator.page(paginator.num_pages)

# 	return render(request,'blogs/post/list.html',{'page':page,'posts':posts})
# 	# posts = Post.published.all()
# 	# return render(request,'blogs/post/list.html',{'posts':posts})

def post_detail(request,year,month,day,post):
	post = get_object_or_404(Post, slug=post,status='published',publish__year=year,publish__month=month,publish__day=day)
	return render(request,'blogs/post/detail.html',{'post':post})


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
