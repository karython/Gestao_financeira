# app/services/pdf_service.py
from fpdf import FPDF
from io import BytesIO
from datetime import datetime


def generate_report_pdf(report_data: dict, user_name: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Relatório Financeiro - {user_name}", ln=True, align='C')
    pdf.ln(10)

    # Informações do período
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Período: {report_data['month']:02d}/{report_data['year']}", ln=True)
    pdf.ln(5)

    # Resumo
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resumo", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Total de Receitas: R$ {report_data['total_income']:.2f}", ln=True)
    pdf.cell(100, 10, txt=f"Total de Despesas: R$ {report_data['total_expense']:.2f}", ln=True)
    pdf.cell(100, 10, txt=f"Saldo: R$ {report_data['balance']:.2f}", ln=True)
    pdf.ln(10)

    # Transações
    if report_data['transactions']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Detalhamento de Transações", ln=True)
        pdf.ln(5)

        # Cabeçalho da tabela
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 10, txt="Data", border=1)
        pdf.cell(70, 10, txt="Descrição", border=1)
        pdf.cell(30, 10, txt="Tipo", border=1)
        pdf.cell(30, 10, txt="Valor", border=1, ln=True)

        # Dados da tabela
        pdf.set_font("Arial", size=10)
        for t in report_data['transactions']:
            pdf.cell(30, 10, txt=str(t['date']), border=1)
            pdf.cell(70, 10, txt=t['description'][:30], border=1)
            pdf.cell(30, 10, txt=t['type'], border=1)
            pdf.cell(30, 10, txt=f"R$ {t['amount']:.2f}", border=1, ln=True)

    # Rodapé
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt=f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align='C')

    buffer = BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
