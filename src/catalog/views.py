from django.shortcuts import render, get_object_or_404
from .models import Book, BookInstance,Author
from django.views import generic
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseForbidden
from catalog.forms import RenewBookForm 
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Create your views here.
def index(request):

	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	#available books (status = 'a')

	num_instances_available = BookInstance.objects.filter(status__iexact='a').count()

	#number of authors

	num_authors = Author.objects.count()

	#number of visits to this view, as counted in the session

	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	context = {

			'num_books': num_books,
			'num_instances': num_instances,
			'num_authors': num_authors,
			'num_instances_available': num_instances_available,
			'num_visits': num_visits,


	}

	return render(request, 'index.html', context)

class BookListView(generic.ListView):
	model = Book
	paginate_by = 10


	def get_context_data(self, **kwargs):
		context = super(BookListView, self).get_context_data(**kwargs)
		context['some_data'] = 'This is just some data'
		return context

class BookDetailView(generic.DetailView):
	model = Book

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get the context
		context = super(BookDetailView, self).get_context_data(**kwargs)
		# Create any data and add it to the context
		context['some_data'] = 'This is just some data'
		return context

class AuthorListView(generic.ListView):
	model = Author

	def get_context_data(self, **kwargs):
		context = super(AuthorListView, self).get_context_data(**kwargs)
		context['some_data'] = 'This is just a random stuff'

		return context
class AuthorDetailView(generic.DetailView):
	model = Author

class LoanBooksByUserListView(LoginRequiredMixin,generic.ListView):
	model = BookInstance
	template_name = 'catalog/BookInstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__iexact='o').order_by('due_back')

class LibBookBorrowedListView(generic.ListView, PermissionRequiredMixin):
	model = BookInstance
	template_name = 'catalog/BookInstance_list_borrowed_for_librarian.html'
	permission_required = 'catalog.can_mark_returned'
	paginate_by = 10


	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
	book_instance = get_object_or_404(BookInstance, pk=pk)

	if request.method == 'POST':
		form = RenewBookForm(request.POST)

		if form.is_valid():
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()


			return HttpResponseRedirect(reverse('all-borrowed'))

	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedeltal(weeks=3)
		form = RenewBookForm(initial={'renewal_date':proposed_renewal_date})

		context={
			'form': form,
			'book_instance': book_instance,

		}

		return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class AuthorCreate(CreateView, PermissionRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Author
	fields = ['first_name', 'last_name','data_of_birth', 'date_of_death']
	initial = {'date_of_death': '11/02/1889'}


class AuthorUpdate(UpdateView, PermissionRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Author
	fields = ['first_name', 'last_name','data_of_birth', 'date_of_death']
class AuthorDelete(DeleteView, PermissionRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Author
	success_url = reverse_lazy('authors')

class BookCreate(CreateView, LoginRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Book
	fields = ['title', 'author','summary','isbn', 'genre']

	# def upload_book_cover(request):
	# 	if request.method =='POST':
	# 		form = ImageUploadForm(request.POST, request.FILES)
	# 		if form.is_valid():
	# 			m = Book.objects.get(pk=book_cover)
	# 			m.book_cover = form.cleaned_data['image']
	# 			m.save()

	# 			return HttpResponse('upload sucessful')
	# 		return HttpResponseForbidden('only images allowed')


class BookUpdate(UpdateView,PermissionRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Book
	fields = [ 'title', 'author','summary','isbn', 'genre']

class BookDelete(DeleteView, PermissionRequiredMixin):
	permissin_required = 'catalog.can_mark_returned'
	model = Book
	success_url = reverse_lazy('books')

# class BorrowBook(generic.UpdateView,PermissionRequiredMixin):
# 	permission_required = 'catalog.can_mark_returned'
# 	model = BookInstance
# 	fields = ['book', 'borrower', 'due_back']

# 	def get_queryset(self):
		
# 		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o')

