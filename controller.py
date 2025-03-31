import pandas as pd
from downloader import PDFDownloader
from processor import PDFProcessor
from config import Config

class ANSController:
    def __init__(self):
        self.downloader = PDFDownloader()
        self.processor = PDFProcessor()
        self.keep_temp_files = False
    
    def set_keep_temp_files(self, keep=True):
        """Define se os arquivos temporários devem ser mantidos."""
        self.keep_temp_files = keep
    
    def process_all(self):
        """Executa todo o fluxo do processo."""
        try:
            # Passo 1: Download dos PDFs
            print("=== Downloader ANS ===")
            pdf_files = self.downloader.download()
            print(f"✅ {len(pdf_files)} arquivos baixados.")
            
            if not pdf_files:
                print("❌ Nenhum arquivo PDF foi baixado.")
                return False
                
            # Passo 2: Processar cada PDF e combinar os resultados
            print("\n=== Processador ANS ===")
            all_dfs = []
            
            for pdf_file in pdf_files:
                df = self.processor.process_pdf(pdf_file)
                if not df.empty:
                    all_dfs.append(df)
            
            if not all_dfs:
                print("❌ Nenhum dado válido foi extraído dos PDFs.")
                return False
                
            # Combina todos os DataFrames
            final_df = pd.concat(all_dfs, ignore_index=True)
            final_df = final_df.drop_duplicates()
            
            # Passo 3: Salvar em Excel
            output_path = self.processor.save_to_excel(final_df)
            print(f"✅ Dados consolidados em: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante o processamento: {str(e)}")
            return False
        finally:
            # Limpar arquivos temporários, se necessário
            if not self.keep_temp_files:
                self.downloader.cleanup()