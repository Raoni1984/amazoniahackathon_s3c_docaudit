import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("sample_docs", exist_ok=True)

def get_fonts():
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 17)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_regular = ImageFont.truetype("arial.ttf", 19)
        font_small = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_bold = font_title
        font_regular = font_title
        font_small = font_title
    return font_title, font_sub, font_bold, font_regular, font_small

def create_embargo_doc():
    w, h = 1200, 1600
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title, font_sub, font_bold, font_regular, font_small = get_fonts()

    # Outer border
    draw.rectangle([(40, 40), (w-40, h-40)], outline=(30, 30, 30), width=3)
    
    # Header box
    draw.rectangle([(40, 40), (w-40, 160)], fill=(240, 245, 242), outline=(30, 30, 30), width=2)
    draw.text((w//2, 65), "GOVERNO DO ESTADO DO PARÁ", fill=(0, 0, 0), font=font_title, anchor="mm")
    draw.text((w//2, 100), "SECRETARIA DE ESTADO DE MEIO AMBIENTE E SUSTENTABILIDADE - SEMAS", fill=(20, 80, 50), font=font_bold, anchor="mm")
    draw.text((w//2, 135), "DIRETORIA DE FISCALIZAÇÃO AMBIENTAL - DIFISC", fill=(50, 50, 50), font=font_sub, anchor="mm")

    # Title
    draw.rectangle([(40, 175), (w-40, 235)], fill=(230, 235, 230), outline=(30, 30, 30), width=2)
    draw.text((w//2, 205), "TERMO DE EMBARGO E INTERDIÇÃO Nº 00412/2026", fill=(150, 0, 0), font=font_bold, anchor="mm")

    y = 260
    # Field 1: Autuado
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "1. IDENTIFICAÇÃO DO AUTUADO / RESPONSÁVEL", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Nome do Autuado: Raimundo Nonato Silveira", fill=(0, 0, 0), font=font_bold)
    draw.text((700, y+35), "CPF: 521.843.902-15", fill=(0, 0, 0), font=font_bold)
    
    y += 100
    # Field 2: Localização & Município
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "2. LOCALIZAÇÃO DO IMÓVEL / JURISDIÇÃO", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Imóvel / Fazenda: Fazenda Serra Dourada - Gleba 04", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+58), "Município: Novo Progresso - PA", fill=(0, 0, 0), font=font_bold)
    draw.text((700, y+58), "Data da Emissão: 12/09/2026", fill=(0, 0, 0), font=font_bold)

    y += 100
    # Field 3: CAR e Área
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "3. DADOS CADASTRAIS E ÁREA EMBARGADA", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Número do CAR: PA-1505035-7C9F4E8D12A34B5C6D7E8F9012345678", fill=(0, 0, 0), font=font_bold)
    draw.text((60, y+58), "Área Embargada (ha): 84.50 ha", fill=(180, 0, 0), font=font_bold)
    draw.text((500, y+58), "Coordenadas: 07°08'42\"S 55°24'18\"W", fill=(0, 0, 0), font=font_bold)

    y += 100
    # Field 4: Descrição e Fundamentação
    draw.rectangle([(50, y), (w-50, y+160)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "4. MOTIVAÇÃO DO EMBARGO / FUNDAMENTAÇÃO LEGAL", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Descrição: Fica embargada a atividade de desmatamento e queima não autorizada", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+60), "de floresta nativa em área de Reserva Legal dentro do bioma Amazônico.", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+90), "Fundamento Legal: Art. 50 do Decreto Federal nº 6.514/2008 e Lei Federal nº 9.605/1998.", fill=(0, 0, 0), font=font_bold)
    draw.text((60, y+120), "Fica o autuado intimado a paralisar imediatamente qualquer supressão vegetal.", fill=(100, 0, 0), font=font_regular)

    y += 180
    # Signatures
    draw.rectangle([(50, y), (w-50, y+140)], fill=(250, 252, 250), outline=(100, 100, 100), width=1)
    draw.line([(80, y+90), (480, y+90)], fill=(0, 0, 0), width=2)
    draw.text((280, y+100), "Paulo Roberto Souza - Matrícula 84920", fill=(0, 0, 0), font=font_regular, anchor="mm")
    draw.text((280, y+120), "Agente Autuante / Fiscal Ambiental SEMAS", fill=(80, 80, 80), font=font_small, anchor="mm")

    draw.line([(650, y+90), (1050, y+90)], fill=(0, 0, 0), width=2)
    draw.text((850, y+100), "Raimundo Nonato Silveira", fill=(0, 0, 0), font=font_regular, anchor="mm")
    draw.text((850, y+120), "Autuado / Notificado", fill=(80, 80, 80), font=font_small, anchor="mm")

    # Footer note
    draw.text((w//2, h-60), "DOCUMENTO PÚBLICO DE FISCALIZAÇÃO AMBIENTAL - CADEIA DE CUSTÓDIA SC3", fill=(120, 120, 120), font=font_small, anchor="mm")

    img.save("sample_docs/01_termo_embargo_novo_progresso.jpg", quality=95)
    print("Generated 01_termo_embargo_novo_progresso.jpg successfully!")

def create_infraction_doc():
    w, h = 1200, 1600
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title, font_sub, font_bold, font_regular, font_small = get_fonts()

    # Outer border
    draw.rectangle([(40, 40), (w-40, h-40)], outline=(30, 30, 30), width=3)
    
    # Header box
    draw.rectangle([(40, 40), (w-40, 160)], fill=(240, 245, 242), outline=(30, 30, 30), width=2)
    draw.text((w//2, 65), "GOVERNO DO ESTADO DO PARÁ", fill=(0, 0, 0), font=font_title, anchor="mm")
    draw.text((w//2, 100), "SECRETARIA DE ESTADO DE MEIO AMBIENTE E SUSTENTABILIDADE - SEMAS", fill=(20, 80, 50), font=font_bold, anchor="mm")
    draw.text((w//2, 135), "DIRETORIA DE FISCALIZAÇÃO AMBIENTAL - AUTO DE INFRAÇÃO", fill=(50, 50, 50), font=font_sub, anchor="mm")

    # Title
    draw.rectangle([(40, 175), (w-40, 235)], fill=(230, 235, 230), outline=(30, 30, 30), width=2)
    draw.text((w//2, 205), "AUTO DE INFRAÇÃO AMBIENTAL Nº 00831/2026", fill=(180, 0, 0), font=font_bold, anchor="mm")

    y = 260
    # Field 1: Autuado
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "1. IDENTIFICAÇÃO DO INFRATOR / AUTUADO", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Autuado / Responsável: Agropecuária Rio Xingu Ltda", fill=(0, 0, 0), font=font_bold)
    draw.text((700, y+35), "CNPJ: 12.345.678/0001-90", fill=(0, 0, 0), font=font_bold)
    
    y += 100
    # Field 2: Localização & Município
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "2. LOCALIZAÇÃO DO FATO / JURISDIÇÃO", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Imóvel / Fazenda: Fazenda Rio Verde - Estrada Triunfo Km 45", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+58), "Município: São Félix do Xingu - PA", fill=(0, 0, 0), font=font_bold)
    draw.text((700, y+58), "Data da Emissão: 12/09/2026", fill=(0, 0, 0), font=font_bold)

    y += 100
    # Field 3: Multa, CAR e Área
    draw.rectangle([(50, y), (w-50, y+80)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "3. DADOS DA INFRAÇÃO, ÁREA E PENALIDADE", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Número do CAR: PA-1507300-8F9E2A1B4C6D8E0F123456789ABCDEF0", fill=(0, 0, 0), font=font_bold)
    draw.text((60, y+58), "Área Desmatada (ha): 142.00 ha", fill=(180, 0, 0), font=font_bold)
    draw.text((450, y+58), "Valor da Multa: R$ 422.500,00", fill=(180, 0, 0), font=font_bold)
    draw.text((800, y+58), "Coordenadas: 06°38'22\"S 51°59'45\"W", fill=(0, 0, 0), font=font_bold)

    y += 100
    # Field 4: Tipificação
    draw.rectangle([(50, y), (w-50, y+160)], outline=(100, 100, 100), width=1)
    draw.text((60, y+10), "4. TIPIFICAÇÃO DA CONDUTA INFRACIONAL", fill=(80, 80, 80), font=font_small)
    draw.text((60, y+35), "Descrição: Desmatar a corte raso 142,0 hectares de floresta nativa em área", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+60), "especialmente protegida sem prévia autorização do órgão ambiental competente.", fill=(0, 0, 0), font=font_regular)
    draw.text((60, y+90), "Fundamento Legal: Art. 50 do Decreto Federal nº 6.514/2008 e Art. 70 da Lei 9.605/98.", fill=(0, 0, 0), font=font_bold)
    draw.text((60, y+120), "Penalidade: Multa simples consolidada e embargo imediato da área desmatada.", fill=(100, 0, 0), font=font_regular)

    y += 180
    # Signatures
    draw.rectangle([(50, y), (w-50, y+140)], fill=(250, 252, 250), outline=(100, 100, 100), width=1)
    draw.line([(80, y+90), (480, y+90)], fill=(0, 0, 0), width=2)
    draw.text((280, y+100), "Marcos Vinicius Alencar - Matrícula 91204", fill=(0, 0, 0), font=font_regular, anchor="mm")
    draw.text((280, y+120), "Fiscal Ambiental SEMAS / DIFISC", fill=(80, 80, 80), font=font_small, anchor="mm")

    draw.line([(650, y+90), (1050, y+90)], fill=(0, 0, 0), width=2)
    draw.text((850, y+100), "Representante Legal Agropecuária Rio Xingu", fill=(0, 0, 0), font=font_regular, anchor="mm")
    draw.text((850, y+120), "Autuado / Notificado", fill=(80, 80, 80), font=font_small, anchor="mm")

    # Footer note
    draw.text((w//2, h-60), "DOCUMENTO PÚBLICO DE FISCALIZAÇÃO AMBIENTAL - CADEIA DE CUSTÓDIA SC3", fill=(120, 120, 120), font=font_small, anchor="mm")

    img.save("sample_docs/02_auto_infracao_sao_felix_do_xingu.jpg", quality=95)
    print("Generated 02_auto_infracao_sao_felix_do_xingu.jpg successfully!")

if __name__ == "__main__":
    create_embargo_doc()
    create_infraction_doc()
