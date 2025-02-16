from django.core.paginator import Paginator

def paginate(queryset, request, per_page=100):
        paginator = Paginator(queryset, per_page)
        page = request.GET.get('page')
        return paginator.get_page(page)