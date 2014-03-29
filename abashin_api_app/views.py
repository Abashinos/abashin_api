import json
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from query_executor import execute

@csrf_exempt
def response_page(request, entity, method):

    if request.method == 'POST':
        request_data = json.loads(request.body, encoding='utf-8')
    else:
        request_data = request.GET.dict()
    response_data = execute(entity, method, request_data)

    return HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type='application/json')



