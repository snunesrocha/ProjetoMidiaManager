import os
import logging
import streamlit as st
from tkinter import Tk, filedialog
from PIL import Image
from imagehash import average_hash
import pandas as pd


from services.database_service import DatabaseService
from services.gallery_service import GalleryService


def show_thumbnail(file_path, caption):
    """Exibe miniatura proporcional (20% do tamanho original)"""
    try:
        img = Image.open(file_path)
        width, height = img.size
        new_size = (int(width * 0.2), int(height * 0.2))  # 20% proporcional
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        st.image(img_resized, caption=caption)
    except Exception as e:
        st.error(f"Erro ao carregar miniatura: {e}")

class ViewerService:
    def __init__(self, db_service: DatabaseService, gallery_service: GalleryService):
        self.db_service = db_service
        self.gallery_service = gallery_service
        logging.info("ViewerService initialized with DatabaseService and GalleryService")

    def run_interface(self):
        st.title("📸 MidiaManager")

        # Menu com abas
        tab1, tab2 = st.tabs(["📂 GRID Cadastro de Mídia", "👤 Cadastro de Pessoa + Vínculos"])

        with tab1:
            self.show_gallery_grid()

        with tab2:
            self.link_person_form()
            st.divider()
            self.manage_people_media()

    # ------------------------------------------------------------
    # Seletor de pastas (via tkinter)
    # ------------------------------------------------------------
    def _select_folder(self):
        root = Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory()
        root.destroy()
        return folder_selected

    # ------------------------------------------------------------
    # GRID de mídias com cabeçalhos e controle de miniatura
    # ------------------------------------------------------------



    def show_gallery_grid(self):
        st.subheader("📂 Registros de Mídias")
        cursor = self.db_service.connection.cursor()
        cursor.execute("""
            SELECT m.id, m.file_name, m.folder, m.hash, p.name
            FROM media m
            LEFT JOIN people_media pm ON m.id = pm.media_id
            LEFT JOIN people p ON pm.person_id = p.id
        """)
        records = cursor.fetchall()

        if not records:
            st.warning("Nenhum registro encontrado.")
            return

        # Converter para DataFrame
        df = pd.DataFrame(records, columns=["ID", "Arquivo", "Pasta", "Hash", "Pessoa vinculada"])

        # Filtros por coluna
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_arquivo = st.text_input("Filtrar por Arquivo")
        with col2:
            filtro_pasta = st.text_input("Filtrar por Pasta")
        with col3:
            filtro_hash = st.text_input("Filtrar por Hash")
        with col4:
            filtro_pessoa = st.text_input("Filtrar por Pessoa")

        # Aplicar filtros
        if filtro_arquivo:
            df = df[df["Arquivo"].str.contains(filtro_arquivo, case=False, na=False)]
        if filtro_pasta:
            df = df[df["Pasta"].str.contains(filtro_pasta, case=False, na=False)]
        if filtro_hash:
            df = df[df["Hash"].str.contains(filtro_hash, case=False, na=False)]
        if filtro_pessoa:
            df = df[df["Pessoa vinculada"].str.contains(filtro_pessoa, case=False, na=False)]

        # Mostrar tabela interativa ocupando 100% da largura
        st.dataframe(df, use_container_width=True)

        # Selecionar uma linha pelo ID
        if not df.empty:
            selected_id = st.selectbox("Selecione um ID para ação", df["ID"].tolist())
            if selected_id:
                row = df[df["ID"] == selected_id].iloc[0]
                file_path = os.path.join(row["Pasta"], row["Arquivo"])
                if os.path.exists(file_path):
                    colA, colB, colC = st.columns([1,1,2])
                    with colA:
                        if st.button("Visualizar miniatura", key=f"view_{selected_id}"):
                            show_thumbnail(file_path, row["Arquivo"])
                    with colB:
                        if st.button("Esconder miniatura", key=f"hide_{selected_id}"):
                            st.empty()
                    with colC:
                        if st.button("Visualizar tamanho normal", key=f"full_{selected_id}"):
                            st.image(Image.open(file_path), caption=row["Arquivo"], width=800)

    # ------------------------------------------------------------
    # Cadastro de pessoa + vínculo com miniatura e botão de tamanho normal
    # ------------------------------------------------------------

    def link_person_form(self):
        st.subheader("🔗 Vincular Pessoa a Imagem")
        cursor = self.db_service.connection.cursor()
        # cursor.execute("SELECT id, file_name, folder FROM media")
        cursor.execute("""SELECT m.id, m.file_name, m.folder, p.name
            FROM media m
            LEFT JOIN people_media pm ON m.id = pm.media_id
            LEFT JOIN people p ON pm.person_id = p.id""")


        records = cursor.fetchall()

        if not records:
            st.info("Nenhuma imagem disponível.")
            return

        # Converter para DataFrame
        df = pd.DataFrame(records, columns=["ID", "Arquivo", "Pasta", "Pessoa vinculada"])

        # Mostrar tabela interativa (100% largura, com ordenação e filtro)
        st.dataframe(df, use_container_width=True)

        # Selecionar uma linha pelo ID
        selected_id = st.selectbox("Selecione um ID para vincular", df["ID"].tolist())
        if selected_id:
            row = df[df["ID"] == selected_id].iloc[0]
            file_path = os.path.join(row["Pasta"], row["Arquivo"])

            # Mostrar miniatura
            if os.path.exists(file_path):
                show_thumbnail(file_path, row["Arquivo"])
                if st.button("Visualizar tamanho normal", key=f"full_{selected_id}_{row['Arquivo']}"):
                    st.image(Image.open(file_path), caption=row["Arquivo"])

            # Campo para nome da pessoa
            person_name = st.text_input("Nome da pessoa")
            if st.button("Vincular", key=f"link_{selected_id}_{row['Arquivo']}"):
                if person_name:
                    with Image.open(file_path) as img:
                        img_hash = str(average_hash(img))
                    self.db_service.insert_person_record(person_name, img_hash)

                    # Buscar pessoa pelo nome ou hash
                    cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
                    row_p = cursor.fetchone()
                    if row_p:
                        person_id = row_p[0]
                    else:
                        cursor.execute("SELECT id FROM people WHERE hash = ?", (img_hash,))
                        row_p = cursor.fetchone()
                        if row_p:
                            person_id = row_p[0]
                        else:
                            st.error("Não foi possível localizar o registro da pessoa.")
                            return

                    # Vincular pessoa à mídia
                    self.db_service.link_person_to_media(person_id, selected_id)
                    st.success(f"✅ Pessoa '{person_name}' vinculada à imagem {row['Arquivo']}")
                else:
                    st.error("Informe o nome da pessoa.")

    # ------------------------------------------------------------
    # Gerenciar vínculos pessoa-mídia
    # ------------------------------------------------------------


    def manage_people_media(self):
        st.subheader("👤 Gerenciar vínculos de pessoas")
        cursor = self.db_service.connection.cursor()
        cursor.execute("SELECT id, name FROM people")
        people = cursor.fetchall()

        if not people:
            st.info("Nenhuma pessoa cadastrada.")
            return

        person_options = {name: pid for pid, name in people}
        selected_person = st.selectbox("Selecione uma pessoa", list(person_options.keys()))

        if selected_person:
            person_id = person_options[selected_person]
            media_records = self.db_service.get_media_by_person(person_id)

            if not media_records:
                st.info(f"Nenhuma mídia vinculada a {selected_person}.")
                return

            # Converter para DataFrame
            df = pd.DataFrame(media_records, columns=["ID", "Arquivo", "Pasta", "LinkID"])

            # Mostrar todas as mídias vinculadas em tabela interativa
            st.dataframe(df, use_container_width=True)

            # Para cada mídia vinculada, mostrar miniatura e botões
            for idx, row in df.iterrows():
                file_path = os.path.join(row["Pasta"], row["Arquivo"])
                if os.path.exists(file_path):
                    show_thumbnail(file_path, row["Arquivo"])

                    colA, colB = st.columns([1,1])
                    with colA:
                        if st.button("Visualizar tamanho normal", key=f"full_{row['ID']}_{row['Arquivo']}"):
                            st.image(Image.open(file_path), caption=row["Arquivo"])
                    with colB:
                        if st.button("Desvincular", key=f"unlink_{row['LinkID']}_{row['Arquivo']}"):
                            self.db_service.unlink_person_from_media(row["LinkID"])
                            st.success(f"Desvinculado {row['Arquivo']} de {selected_person}")
