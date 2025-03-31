from controller import ANSController
import argparse

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="ANS PDF Downloader and Processor")
    parser.add_argument("--keep-temp", action="store_true", 
                        help="Mantém os arquivos PDF temporários após o processamento")
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    print("=== ANS Scraping e Processamento ===")
    controller = ANSController()
    
    # Configurar para manter arquivos temporários, se solicitado
    if args.keep_temp:
        controller.set_keep_temp_files(True)
        print("Arquivos temporários serão mantidos após o processamento.")
    
    # Executar o fluxo completo
    success = controller.process_all()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Processo concluído com erros.")

if __name__ == "__main__":
    main()