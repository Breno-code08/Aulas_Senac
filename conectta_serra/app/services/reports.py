from io import StringIO, BytesIO
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from flask import Response
from app.services.common import now

def safe_cell(value):
    value = str(value or '')
    return "'" + value if value.startswith(('=', '+', '-', '@', '\t', '\r')) else value

def export_report(records, format, filters):
    if format == 'csv':
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Nº', 'Cliente', 'Profissional', 'Serviço', 'Status', 'Data solicitada', 'Bairro', 'Valor de referência'])
        for r in records:
            writer.writerow([safe_cell(r[k]) for k in ['id','client_name','professional_name','title','status','preferred_date','neighborhood','price']])
        return Response('\ufeff' + output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename="conectta-relatorio.csv"'})
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setTitle('Conectta Serra — Relatório de solicitações')
    y = 790
    lines = ['CONECTTA SERRA | Relatório de solicitações',
             'Demonstração acadêmica — dados fictícios', 'Gerado em: ' + now()[:10],
             'Status: ' + (filters.get('status') or 'todos'),
             'Cadastro: ' + (filters.get('from') or 'início') + ' a ' + (filters.get('to') or 'hoje'),
             f'Registros: {len(records)}', '']
    for r in records:
        lines.extend([f"#{r['id']} — {r['status']} — {r['preferred_date']}",
                      f"{r['client_name']} > {r['professional_name']}",
                      f"{r['title']} | {r['neighborhood']} | Ref.: R$ {r['price']:.2f}", ''])
    for line in lines:
        if y < 50:
            pdf.showPage()
            y = 790
        pdf.setFont('Helvetica', 10)
        # Bound a displayed line; full record strings remain available in CSV.
        pdf.drawString(40, y, line[:105])
        y -= 16
    pdf.save()
    return Response(output.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename="conectta-relatorio.pdf"'})
