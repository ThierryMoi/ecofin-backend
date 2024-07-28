from pymilvus import Collection, connections
import os
from dotenv import load_dotenv

load_dotenv()

MILVUS_PORT_DEV=os.environ.get("MILVUS_PORT_DEV")
MILVUS_HOST_DEV=os.environ.get("MILVUS_HOST_DEV")
COLLECTION_ARTICLE_NAME_DEV=str(os.environ.get("COLLECTION_ARTICLE_NAME_DEV"))

NB_ART=int(os.environ.get("NB_ART"))
VOISIN=int(os.environ.get("VOISIN"))
NB_RAPPORT=int(os.environ.get("NB_RAPPORT"))
URL_1024=os.environ.get("URL_1024")


connections.connect(alias="defaultdev", host=MILVUS_HOST_DEV, port=MILVUS_PORT_DEV)



index_params = {
    "metric_type": "IP",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024},
}

###########################################################################################""
COLLECTION_ARTICLE_DEV = Collection(name=COLLECTION_ARTICLE_NAME_DEV)

COLLECTION_ARTICLE_DEV.create_index("paragraphe_embedding", index_params)
COLLECTION_ARTICLE_DEV.create_index("title_embedding", index_params)
COLLECTION_ARTICLE_DEV.create_index("time_embedding", index_params)
COLLECTION_ARTICLE_DEV.load()

