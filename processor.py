import pandas as pd
import re
from tabula.io import read_pdf
from config import Config

class PDFProcessor:
    def __init__(self):
        self.output_excel = Config.OUTPUT_EXCEL
    
    @staticmethod
    def clean_text(text):
        """Remove caracteres especiais e espaços extras do texto."""
        if pd.isna(text):
            return ""
        text = str(text)
        # Remove múltiplos espaços, quebras de linha e caracteres especiais
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_tables_from_pdf(self, pdf_path):
        """Extrai todas as tabelas do PDF e as concatena em um único DataFrame."""
        # Lê todas as tabelas do PDF
        dfs = read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True)
        
        # Filtra e limpa as tabelas
        cleaned_dfs = []
        for df in dfs:
            if df.shape[1] < 5:  # Ignora tabelas com poucas colunas (provavelmente não são dados principais)
                continue
            
            # Limpa os nomes das colunas
            df.columns = [self.clean_text(col) for col in df.columns]
            
            # Remove linhas totalmente vazias
            df = df.dropna(how='all')
            
            cleaned_dfs.append(df)
        
        # Concatena todas as tabelas em uma única
        if cleaned_dfs:
            final_df = pd.concat(cleaned_dfs, ignore_index=True)
        else:
            final_df = pd.DataFrame()
        
        return final_df

    def process_procedures_data(self, raw_df):
        """Processa o DataFrame bruto para o formato desejado."""
        # Renomeia colunas para o padrão desejado (ajuste conforme necessário)
        column_mapping = {
            'PROCEDIMENTO': 'Procedimento',
            'RN (alteração)': 'RN',
            'VIGÊNCIA': 'Vigência',
            'OD': 'OD',
            'AMB': 'AMB',
            'HCO': 'HCO',
            'HSO': 'HSO',
            'REF': 'REF',
            'PAC': 'PAC',
            'DUT': 'DUT',
            'SUBGRUPO': 'Subgrupo',
            'GRUPO': 'Grupo',
            'CAPÍTULO': 'Capítulo'
        }
        
        # Renomeia as colunas
        raw_df = raw_df.rename(columns=column_mapping)
        
        # Mantém apenas as colunas de interesse
        desired_columns = [
            'Procedimento', 'RN', 'Vigência', 'OD', 'AMB', 'HCO', 
            'HSO', 'REF', 'PAC', 'DUT', 'Subgrupo', 'Grupo', 'Capítulo'
        ]
        
        # Filtra colunas existentes (pode não ter todas)
        available_columns = [col for col in desired_columns if col in raw_df.columns]
        
        # Filtra colunas e remove duplicatas
        processed_df = raw_df[available_columns].copy()
        processed_df = processed_df.drop_duplicates()
        
        # Limpa os dados
        for col in processed_df.columns:
            processed_df[col] = processed_df[col].apply(self.clean_text)
        
        return processed_df

    def save_to_excel(self, df, output_path=None):
        """Salva o DataFrame em um arquivo Excel."""
        if output_path is None:
            output_path = self.output_excel
            
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Dados salvos em: {output_path}")
        return output_path

    def process_pdf(self, pdf_path):
        """Processa um único PDF e retorna o DataFrame."""
        print(f"Extraindo tabelas do PDF: {pdf_path}")
        raw_df = self.extract_tables_from_pdf(pdf_path)
        
        if raw_df.empty:
            print(f"Nenhuma tabela válida encontrada no PDF: {pdf_path}")
            return pd.DataFrame()
        
        print("Processando dados...")
        processed_df = self.process_procedures_data(raw_df)
        return processed_df