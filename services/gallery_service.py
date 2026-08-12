import os
import shutil
import logging
from PIL import Image
import imagehash

from services.database_service import DatabaseService

class GalleryService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        logging.info("GalleryService initialized with DatabaseService")

    def process_folders(self, folder1: str, folder2: str, output_folder: str):
        logging.info(f"Processing folders: {folder1}, {folder2}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            logging.info(f"Created output folder: {output_folder}")

        unique_hashes = {}
        for folder in [folder1, folder2]:
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                try:
                    with Image.open(file_path) as img:
                        img_hash = str(imagehash.average_hash(img))
                        if img_hash not in unique_hashes:
                            unique_hashes[img_hash] = file_name
                            shutil.copy(file_path, output_folder)
                            logging.info(f"Copied unique file: {file_name}")
                            self.db_service.insert_media_record(file_name, img_hash, output_folder)
                        else:
                            logging.info(f"Duplicate found: {file_name}")
                except Exception as e:
                    logging.error(f"Error processing file {file_name}: {e}")
        logging.info("Folder processing completed")

    def catalog_people(self, image_path: str, person_name: str):
        try:
            with Image.open(image_path) as img:
                img_hash = str(imagehash.average_hash(img))
            self.db_service.insert_person_record(person_name, img_hash)
            logging.info(f"Person {person_name} cataloged for image {image_path}")
        except Exception as e:
            logging.error(f"Error cataloging person {person_name} in {image_path}: {e}")

    def identify_person(self, image_path: str):
        try:
            with Image.open(image_path) as img:
                img_hash = str(imagehash.average_hash(img))
            person = self.db_service.get_person_by_hash(img_hash)
            if person:
                logging.info(f"Person identified: {person}")
                return person
            else:
                logging.info("No person identified for this image")
                return None
        except Exception as e:
            logging.error(f"Error identifying person in {image_path}: {e}")
            return None
