import logging
import streamlit as st

from services.database_service import DatabaseService
from services.gallery_service import GalleryService
from services.viewer_service import ViewerService

# ============================================================
# MidiaManager - Main
# Ponto de entrada do sistema
# ============================================================

def main():
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logging.info("Starting MidiaManager application")

    # Inicialização dos serviços
    db_service = DatabaseService()
    gallery_service = GalleryService(db_service)
    viewer_service = ViewerService(db_service, gallery_service)

    # Executar interface Streamlit
    viewer_service.run_interface()

    # Encerramento
    db_service.close()
    logging.info("MidiaManager application finished")

if __name__ == "__main__":
    main()
