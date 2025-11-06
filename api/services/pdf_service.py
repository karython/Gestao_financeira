# app/services/pdf_service.py
from fpdf import FPDF
from io import BytesIO
from datetime import datetime


class StyledPDF(FPDF):
    def header(self):
        # Cor de fundo do cabeçalho
        self.set_fill_color(50, 90, 160)  # Azul escuro
        self.rect(0, 0, 210, 30, 'F')

        # Título branco centralizado
        self.set_font("Arial", 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Relatório Financeiro", align='C', ln=True)
        self.ln(5)

        # Linha divisória
        self.set_draw_color(255, 255, 255)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", align='C')


def generate_report_pdf(report_data: dict, user_name: str) -> bytes:
    pdf = StyledPDF()
    pdf.add_page()

    # === Cabeçalho do Relatório (Estilo Image 2) ===
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 16)
    # Título centralizado com nome do usuário
    pdf.cell(0, 10, f"Relatório Financeiro - {user_name}", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Período: {report_data['month']:02d}/{report_data['year']}", ln=True, align='C')
    pdf.ln(5)

    # Adicionar categoria selecionada
    if 'category' in report_data:
        pdf.cell(0, 10, f"Categoria: {report_data['category']}", ln=True, align='C')
    pdf.ln(5)

    # Data e hora de geração
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Gerado por: {user_name} em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    # === Caixa de Resumo (Estilo Image 2) ===
    # Esta caixa usa células com bordas para criar o efeito de "caixa"

    pdf.set_font("Arial", 'B', 12)

    # Definir larguras e posição
    label_width = 70
    value_width = 50
    total_width = label_width + value_width
    start_x = (pdf.w - total_width) / 2 # Centralizar a caixa

    # Cores aprimoradas
    border_color = (100, 100, 100)
    fill_color_light = (240, 248, 255)  # Azul claro
    fill_color_white = (255, 255, 255)
    header_fill = (70, 130, 180)  # Azul médio

    pdf.set_draw_color(*border_color)
    pdf.set_line_width(0.5)

    # Cabeçalho da caixa
    pdf.set_fill_color(*header_fill)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(start_x, pdf.get_y())
    pdf.cell(total_width, 12, "Resumo Financeiro", border=1, align='C', fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)

    # --- Linha 1: Receitas ---
    pdf.set_fill_color(*fill_color_light)
    pdf.set_x(start_x)
    pdf.cell(label_width, 10, "Total de Receitas:", border=1, align='L', fill=True)

    pdf.set_text_color(34, 139, 34)  # Verde escuro
    pdf.cell(value_width, 10, f"R$ {report_data['total_income']:.2f}", border=1, align='R', fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)

    # --- Linha 2: Despesas ---
    pdf.set_fill_color(*fill_color_white)
    pdf.set_x(start_x)
    pdf.cell(label_width, 10, "Total de Despesas:", border=1, align='L', fill=True)

    pdf.set_text_color(220, 20, 60)  # Vermelho escuro
    pdf.cell(value_width, 10, f"R$ {report_data['total_expense']:.2f}", border=1, align='R', fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)

    # --- Linha 3: Saldo ---
    balance_color = (34, 139, 34) if report_data['balance'] >= 0 else (220, 20, 60)
    pdf.set_fill_color(*fill_color_light)
    pdf.set_x(start_x)

    pdf.cell(label_width, 10, "Saldo:", border=1, align='L', fill=True)

    pdf.set_text_color(*balance_color)
    pdf.cell(value_width, 10, f"R$ {report_data['balance']:.2f}", border=1, align='R', fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)

    pdf.ln(20)  # Espaçamento maior


    # === Tabela de Transações (Estilo Excel-like) ===
    if report_data['transactions']:
        pdf.set_font("Arial", 'B', 14)
        # Título "Detalhamento de Transações" (de Image 2)
        pdf.cell(0, 12, "Detalhamento de Transações", ln=True, align='L')
        pdf.ln(5)

        # Cabeçalho da tabela (Azul escuro, estilo Excel)
        pdf.set_fill_color(70, 130, 180)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(70, 130, 180)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_line_width(0.5)

        # Colunas (Data, Descrição, Tipo, Valor)
        # Bordas completas para estilo Excel
        pdf.cell(35, 12, "Data", border=1, align='C', fill=True)
        pdf.cell(85, 12, "Descrição", border=1, align='C', fill=True)
        pdf.cell(35, 12, "Tipo", border=1, align='C', fill=True)
        pdf.cell(35, 12, "Valor (R$)", border=1, align='C', fill=True, ln=True)

        # Resetar estilos para as linhas de dados
        pdf.set_line_width(0.3)
        pdf.set_draw_color(100, 100, 100)  # Bordas cinzas escuras
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        fill = False

        color_income = (34, 139, 34)  # Verde escuro
        color_expense = (220, 20, 60)  # Vermelho escuro
        color_default = (0, 0, 0)

        row_fill_light = (248, 248, 248)  # Cinza muito claro
        row_fill_white = (255, 255, 255)

        for t in report_data['transactions']:
            # Zebra striping (fundo alternado)
            pdf.set_fill_color(*row_fill_light) if fill else pdf.set_fill_color(*row_fill_white)
            fill = not fill

            pdf.set_text_color(*color_default)

            # Células com bordas completas (estilo Excel)
            pdf.cell(35, 10, str(t['date']), border=1, align='C', fill=True)

            desc = t['description']
            if len(desc) > 45:
                desc = desc[:42] + "..."
            pdf.cell(85, 10, desc, border=1, align='L', fill=True)

            pdf.cell(35, 10, t['type'], border=1, align='C', fill=True)

            # Cor condicional para valor
            cell_color = color_default
            if t['type'].lower() == 'receita':
                cell_color = color_income
            elif t['type'].lower() == 'despesa':
                cell_color = color_expense

            pdf.set_text_color(*cell_color)
            pdf.cell(35, 10, f"{t['amount']:.2f}", border=1, align='R', fill=True, ln=True)

            pdf.set_text_color(*color_default)
            
    else:
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(0, 10, "Nenhuma transação registrada neste período.", ln=True, align='C')

    # === Geração do PDF em memória ===
    buffer = BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes