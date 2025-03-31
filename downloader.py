import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
import shutil
from config import Config

class PDFDownloader:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.temp_dir = Config.TEMP_DIR
        self.output_zip = Config.OUTPUT_ZIP
    
    def _create_temp_dir(self):
        """Cria diretório temporário se não existir"""
        os.makedirs(self.temp_dir, exist_ok=True)

    def _get_pdf_links(self):
        """Coleta links dos Anexos I e II"""
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return [
            link['href'] if link['href'].startswith('http') else f'https://www.gov.br{link["href"]}'
            for link in soup.find_all('a', href=True)
            if ('Anexo I' in link.text or 'Anexo II' in link.text) and link['href'].endswith('.pdf')
        ][:2]  # Garante apenas 2 links

    def _download_file(self, url, filename):
        """Baixa um arquivo para a pasta temporária"""
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)

    def _compress_files(self):
        """Compacta os PDFs em ZIP"""
        with ZipFile(self.output_zip, 'w') as zipf:
            for file in os.listdir(self.temp_dir):
                zipf.write(os.path.join(self.temp_dir, file), file)

    def cleanup(self):
        """Remove arquivos temporários"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def get_downloaded_files(self):
        """Retorna lista de arquivos baixados"""
        if not os.path.exists(self.temp_dir):
            return []
        return [os.path.join(self.temp_dir, f) for f in os.listdir(self.temp_dir)]

    def download(self):
        """Baixa os PDFs e retorna os caminhos dos arquivos"""
        self._create_temp_dir()
        downloaded_files = []
        
        # Download
        for i, link in enumerate(self._get_pdf_links()):
            dest_file = os.path.join(self.temp_dir, f"anexo_{i+1}.pdf")
            print(f"Baixando {dest_file}...")
            self._download_file(link, dest_file)
            downloaded_files.append(dest_file)
        
        # Compactação opcional
        if self.output_zip:
            print("Compactando arquivos...")
            self._compress_files()
        
        return downloaded_files