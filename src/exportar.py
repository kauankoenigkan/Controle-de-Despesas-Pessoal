import csv
import os

def exportar_para_csv(dados, periodo):
    """
    Exporta os lançamentos para um arquivo CSV totalmente compatível com o Excel.
    """
    if not dados:
        return False, f"⚠️ Nenhum lançamento encontrado para o período {periodo}."

    nome_arquivo = f"historico_{periodo}.csv"
    
    try:
        caminho_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(caminho_downloads):
            caminho_completo = os.path.join(caminho_downloads, nome_arquivo)
        else:
            caminho_completo = nome_arquivo

        with open(caminho_completo, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Tipo", "Categoria", "Descrição", "Valor (R$)", "Data"])
            for linha in dados:
                writer.writerow(linha)

        try:
            os.startfile(caminho_completo)
        except Exception:
            pass

        return True, f"✅ Salvo em Downloads: {nome_arquivo}"
    except Exception as err:
        return False, f"❌ Erro ao exportar: {err}"