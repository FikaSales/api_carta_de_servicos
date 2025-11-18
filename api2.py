import requests
import openpyxl
from os import path

# URL da API
url = "https://servicos.ba.gov.br/api/servicossecretaria/17"

# Requisição GET
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    servicos = response.json()

    # Cria uma nova planilha Excel se não existir
    # if not path.exists('servicos_detran_bahia.xlsx'):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Serviços DETRAN"

    # Cabeçalho
    ws.append(["ID", "Nome do Serviço"])
    # Adiciona os dados filtrados
    for servico in servicos:
        ws.append([servico.get("id"), servico.get("nome")])
    # Ajusta largura da coluna
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2
    # Cria planilha para postos e insere cabeçalho
    wb_postos = wb.create_sheet(title='Serviços por Posto')
    wb_postos.append(["ID Serviço", "Serviço", "ID Posto", "Nome Posto", "Municipio"])

    # Add dados dos postos
    for servico in servicos:
        servico_id = servico.get("id")
        servico_nome = servico.get("nome")
        etapas = servico.get("etapas", [])
        for etapa in etapas:
            postos = etapa.get("canal_presencial", [])
            for posto in postos:
                wb_postos.append([
                    servico_id,
                    servico_nome,
                    posto.get("id"),
                    posto.get("nome"),
                    posto.get("municipio")
                ])
    # Salva o arquivo
    wb.save("servicos_detran_bahia.xlsx")
    print("Planilha Serviços criada com sucesso!")
    # else:
        # print("Arquivo já existe: servicos_detran_bahia.xlsx")
else:
    print(f"Erro ao acessar a API: {response.status_code}")