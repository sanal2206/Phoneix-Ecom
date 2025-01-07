from django.http import HttpResponse
from xhtml2pdf import pisa
import pandas as pd

def export_to_excel(data, file_name='report.xlsx'):
    df = pd.DataFrame([data])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    df.to_excel(response, index=False)
    return response

def export_to_pdf(html_content, file_name='report.pdf'):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_content + '</pre>')
    return response
