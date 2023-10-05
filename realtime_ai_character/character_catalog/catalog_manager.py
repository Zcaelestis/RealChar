# this file is used to load characters from the character_catalog directory and load characters from the sql database
# the class is a singleton class, which means that there is only one instance of the class in the whole program
# there are several methods in the class, the most important one is load_characters, which is used to load characters from the character_catalog directory
# the load_characters_from_community method is used to load characters from the community directory
# catalogmanager uses several external libraries
import os
import threading
import time
import yaml
from pathlib import Path
from contextlib import ExitStack

from dotenv import load_dotenv
from firebase_admin import auth
from llama_index import SimpleDirectoryReader
from langchain.text_splitter import CharacterTextSplitter

from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Singleton, Character
from realtime_ai_character.database.chroma import get_chroma
from readerwriterlock import rwlock
from realtime_ai_character.database.connection import get_db
from realtime_ai_character.models.character import Character as CharacterModel

load_dotenv()
logger = get_logger(__name__)


# catalogmanager is a singleton class that is used to manage character catalog;
# it can load characters from the character_catalog directory; 
# and load characters from the sql database;
# and add new characters to the catalog;
#attributes:
#db: the chroma database
#sql_db: the sql database
#sql_load_interval: : An integer representing the interval time in seconds at which to load data from the SQL database.
#sql_load_lock: A reader-writer lock used to synchronize access to the SQL database.
#characters: A dictionary of characters, index keyed by character ID.
#author_name_cache: A dictionary of author names, index keyed by author ID.
class CatalogManager(Singleton): 
    #create a singleton instance of the class
    #Args: overwrite: if True, overwrite existing data in the chroma.
    def __init__(self, overwrite=True):   
        super().__init__()
        self.db = get_chroma() 
        self.sql_db = next(get_db())
        self.sql_load_interval = 30
        self.sql_load_lock = rwlock.RWLockFair()
        #如果overwrite为True,则删除chroma中的所有数据
        if overwrite:
            logger.info('Overwriting existing data in the chroma.')
            self.db.delete_collection()
            self.db = get_chroma()
        # create a dictionary of characters
        self.characters = {}
        self.author_name_cache = {}  
        self.load_characters_from_community(overwrite)    # load characters from the community directory
        self.load_characters(overwrite)                   
      # 如果overwrite为True,则将数据persist到chroma中
        if overwrite:
            logger.info('Persisting data in the chroma.')
            self.db.persist()
        logger.info(
            f"Total document load: {self.db._client.get_collection('llm').count()}")
        self.run_load_sql_db_thread = True
        self.load_sql_db_thread = threading.Thread(target=self.load_sql_db_loop)
        self.load_sql_db_thread.daemon = True
        self.load_sql_db_thread.start()
    # load characters from the sql database
    def load_sql_db_loop(self): 
        while self.run_load_sql_db_thread:  
            self.load_character_from_sql_database()
            time.sleep(self.sql_load_interval) 
   # stop loading characters from the sql database
    def stop_load_sql_db_loop(self):
        self.run_load_sql_db_thread = False
   # get a character from the catalog
    def get_character(self, name) -> Character: 
        with self.sql_load_lock.gen_rlock():
            return self.characters.get(name)
    # load a character from the character_catalog directory
    def load_character(self, directory):  # load a character from the character_catalog directory
        with ExitStack() as stack:        # use ExitStack to ensure that all files are closed
            f_yaml = stack.enter_context(open(directory / 'config.yaml')) # open the config.yaml file
            yaml_content = yaml.safe_load(f_yaml)  # load the yaml file

        character_id = yaml_content['character_id']
        character_name = yaml_content['character_name']
        voice_id =str(yaml_content['voice_id'])
        if (os.getenv(character_id.upper() + "_VOICE_ID", "")):
            voice_id = os.getenv(character_id.upper() + "_VOICE_ID")
        self.characters[character_id] = Character(
            character_id=character_id,
            name=character_name,
            llm_system_prompt=yaml_content["system"],
            llm_user_prompt=yaml_content["user"],
            voice_id=voice_id,
            source='default',
            location='repo',
            visibility='public',
            tts=yaml_content["text_to_speech_use"]
        ) # create a character object, which has the character id, name...

        if "avatar_id" in yaml_content: 
            self.characters[character_id].avatar_id = yaml_content["avatar_id"]       # if the avatar id is in the yaml file get the avatar id from the yaml file
        if "author_name" in yaml_content:
            self.characters[character_id].author_name = yaml_content["author_name"],  # if the author name is in the yaml file get the author name from the yaml file

        return character_name                                                         # return the character name
    # load characters from the character_catalog directory
    def load_characters(self, overwrite):                                             
        """
        Load characters from the character_catalog directory. Use /data to create
        documents and add them to the chroma.

        :overwrite: if True, overwrite existing data in the chroma.
        """
        path = Path(__file__).parent  # get the path of the character_catalog directory

        
        excluded_dirs = {'__pycache__', 'archive', 'community'} # create a set of excluded directories

        directories = [d for d in path.iterdir() if d.is_dir()
                       and d.name not in excluded_dirs]         # get the directories in the character_catalog directory
        # load characters from the character_catalog directory, for each directory in the directories, 
        # if overwrite is True, load the character from the directory, or leave it empty
        for directory in directories:   
            character_name = self.load_character(directory) # load the character from the directory
            if overwrite:                                    # if overwrite is True       
                self.load_data(character_name, directory / 'data')  # load data for the character
                logger.info('Loaded data for character: ' + character_name) # log the message and the character name
        logger.info(
            f'Loaded {len(self.characters)} characters: IDs {list(self.characters.keys())}')   #load the number of characters and their ids
    # load characters from the community directory
    def load_characters_from_community(self, overwrite): 
        path = Path(__file__).parent / 'community'
        excluded_dirs = {'__pycache__', 'archive'}

        directories = [d for d in path.iterdir() if d.is_dir()
                       and d.name not in excluded_dirs]
        for directory in directories:
            with ExitStack() as stack:
                f_yaml = stack.enter_context(open(directory / 'config.yaml'))
                yaml_content = yaml.safe_load(f_yaml)
            character_id = yaml_content['character_id']
            character_name = yaml_content['character_name']
            self.characters[character_id] = Character(
                character_id=character_id,
                name=character_name,
                llm_system_prompt=yaml_content["system"],
                llm_user_prompt=yaml_content["user"],
                voice_id=str(yaml_content["voice_id"]),
                source='community',
                location='repo',
                author_name=yaml_content["author_name"],
                visibility=yaml_content["visibility"],
                tts=yaml_content["text_to_speech_use"]
            )

            if "avatar_id" in yaml_content:
                self.characters[character_id].avatar_id = yaml_content["avatar_id"]

            if overwrite:
                self.load_data(character_name, directory / 'data')
                logger.info('Loaded data for character: ' + character_name)
   # add a new character to the catalog
    def load_data(self, character_name: str, data_path: str): 
        loader = SimpleDirectoryReader(Path(data_path))
        documents = loader.load_data()
        text_splitter = CharacterTextSplitter(
            separator='\n',
            chunk_size=500,
            chunk_overlap=100)
        docs = text_splitter.create_documents(
            texts=[d.text for d in documents],
            metadatas=[{
                'character_name': character_name,
                'id': d.id_,
            } for d in documents])
        self.db.add_documents(docs)

    # load characters from the sql database
    def load_character_from_sql_database(self):
        logger.info('Started loading characters from SQL database')
        character_models = self.sql_db.query(CharacterModel).all()

        with self.sql_load_lock.gen_wlock():
            # delete all characters with location == 'database'
            keys_to_delete = []
            for character_id in self.characters.keys():
                if self.characters[character_id].location == 'database':
                    keys_to_delete.append(character_id)
            for key in keys_to_delete:
                del self.characters[key]

            # add all characters from sql database
            for character_model in character_models: # for each character model in the character models
                if character_model.author_id not in self.author_name_cache:
                    author_name = auth.get_user(
                        character_model.author_id).display_name if os.getenv(
                            'USE_AUTH', '') else "anonymous author"
                    self.author_name_cache[character_model.author_id] = author_name 
                     #if the author id is not in the author name cache, get the author name from the firebase, or use anonymous author
                else:
                    author_name = self.author_name_cache[character_model.author_id] #or get the author name from the author name cache
                    # create a character object
                    # which has the character id, name...
                character = Character(
                    character_id=character_model.id,
                    name=character_model.name,
                    llm_system_prompt=character_model.system_prompt,
                    llm_user_prompt=character_model.user_prompt,
                    voice_id=character_model.voice_id,
                    source='community',
                    location='database',
                    author_id=character_model.author_id,
                    author_name=author_name,
                    visibility=character_model.visibility,
                    tts=character_model.tts,
                    data=character_model.data,
                    avatar_id=character_model.avatar_id if character_model.avatar_id else None
                )  
                self.characters[character_model.id] = character  # add the character to the characters dictionary
                # TODO: load context data from storage           # load context data from storage
        logger.info(
            f'Loaded {len(character_models)} characters from sql database')  
# get the catalog manager
def get_catalog_manager():   
    return CatalogManager.get_instance() # get the singleton instance of the class


if __name__ == '__main__': # if the file is run directly
    manager = CatalogManager.get_instance() # get the singleton instance of the class
