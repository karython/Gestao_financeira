# app/services/pdf_service.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime


def generate_report_pdf(report_data: dict, user_name: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph(f"<b>Relatório Financeiro - {user_name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Informações do período
    period_text = f"Período: {report_data['month']:02d}/{report_data['year']}"
    elements.append(Paragraph(period_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Resumo
    summary_data = [
        ['Total de Receitas:', f"R$ {report_data['total_income']:.2f}"],
        ['Total de Despesas:', f"R$ {report_data['total_expense']:.2f}"],
        ['Saldo:', f"R$ {report_data['balance']:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Transações
    if report_data['transactions']:
        elements.append(Paragraph("<b>Detalhamento de Transações</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        trans_data = [['Data', 'Descrição', 'Tipo', 'Valor']]
        for t in report_data['transactions']:
            trans_data.append([
                str(t['date']),
                t['description'][:30],
                t['type'],
                f"R$ {t['amount']:.2f}"
            ])
        
        trans_table = Table(trans_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(trans_table)
    
    # Rodapé
    elements.append(Spacer(1, 0.5*inch))
    footer = Paragraph(f"<i>Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>", styles['Normal'])
    elements.append(footer)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
