from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    """
    Builds and returns a query string by modifying or adding new parameters to the
    existing query parameters in a request. It ensures proper handling of query
    parameters, including removing unwanted or empty parameters, and specifically
    removes the page parameter if its value is `1`.

    :param context: The context provided by the template tag that contains the
                    HTTP request data, including the existing GET parameters.
                    Expected to have `request` key holding the HTTP request object.
    :type context: dict
    :param kwargs: Arbitrary keyword arguments representing the parameters to be
                   updated or added to the query string. Pass `None` or an empty
                   value to remove a parameter.
    :return: A string representing the modified query parameters, prefixed with
             '&' if there are query parameters; otherwise, an empty string.
    :rtype: str
    """
    query = context['request'].GET.copy()

    for key, value in kwargs.items():
        if value:
            query[key] = value
        elif key in query:
            del query[key]

    if 'page' in query and query['page'] == '1':
        del query['page']

    return '&' + query.urlencode() if query else ''


@register.simple_tag(takes_context=True)
def pagination_url(context, page_num):
    """
    Generates a URL string for pagination by updating the query parameters with
    the provided page number.

    This function uses the Django template tag system and is intended to be used
    in templates. The function adjusts the current request's query parameters to
    include the specified page number, facilitating navigation between pages.

    :param context: The template context, which must include the current request.
                    This typically provides request details, including query
                    parameters.
    :type context: django.template.Context

    :param page_num: The page number to be set in the query parameters for the URL.
    :type page_num: int

    :return: A URL string that includes the updated query parameters with the
             specified page number.
    :rtype: str
    """
    query = context['request'].GET.copy()
    query['page'] = page_num

    return '?' + query.urlencode()


@register.inclusion_tag('pagination/pagination.html', takes_context=True)
def render_pagination(context, page_obj, item_name='елементів'):
    """
    Renders a pagination block to be included in a template. This function processes the request
    and prepares the context needed to display a paginated view, using the specified pagination HTML template.

    :param context: The template context dictionary. Must include a 'request' key with the current
        HTTP request object.
    :type context: dict
    :param page_obj: The page object representing a specific page of items to be rendered.
    :type page_obj: django.core.paginator.Page
    :param item_name: A string representing the type or name of the items in plural form. Defaults to 'елементів'.
    :type item_name: str
    :return: A dictionary prepared for rendering the pagination view in the template. Includes the
        `page_obj`, `item_name`, `query_params` string for extra query parameters, and the `request` object.
    :rtype: dict
    """
    request = context['request']
    query = request.GET.copy()

    if 'page' in query:
        del query['page']

    query_params = '&' + query.urlencode() if query else ''

    return {
        'page_obj': page_obj,
        'item_name': item_name,
        'query_params': query_params,
        'request': request,
    }
