import json
import os

# ==============================================================
# COLOQUE A LOCALIZAÇÃO DO SEU ARQUIVO AQUI:
# Exemplo: 'C:/Users/Nome/Downloads/seu_arquivo.json' ou apenas o nome se estiver na mesma pasta
CAMINHO_DO_ARQUIVO = 'data/teaching-with-moodle_STT 2.json'

# Liste os IDs que você deseja extrair
IDS_DESEJADOS = [10464, 8288, 6744, 5282, 1]
# ==============================================================

def filtrar_e_dividir_cursos(caminho_origem, ids_desejados):
    try:
        # Pega a pasta onde o arquivo original está para salvar os novos lá também
        diretorio = os.path.dirname(os.path.abspath(caminho_origem))
        
        with open(caminho_origem, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        encontrados = 0

        for curso in dados:
            if curso.get('courseid') in ids_desejados:
                course_id = curso['courseid']
                nome_saida = f'metodo2-curso{course_id}.json'
                caminho_saida = os.path.join(diretorio, nome_saida)
                
                with open(caminho_saida, 'w', encoding='utf-8') as f_out:
                    json.dump(curso, f_out, indent=4, ensure_ascii=False)
                
                print(f"✅ Criado: {nome_saida}")
                encontrados += 1
        
        if encontrados == 0:
            print("❌ Nenhum dos IDs foi encontrado dentro do arquivo informado.")
        else:
            print(f"\nPronto! {encontrados} arquivos gerados em: {diretorio}")

    except FileNotFoundError:
        print(f"❌ Erro: O arquivo não foi encontrado no caminho: {caminho_origem}")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")

# Executa o script
if __name__ == "__main__":
    filtrar_e_dividir_cursos(CAMINHO_DO_ARQUIVO, IDS_DESEJADOS)