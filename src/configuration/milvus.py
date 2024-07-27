from pymilvus import Collection, connections
import os
from dotenv import load_dotenv

load_dotenv()

MILVUS_PORT=os.environ.get("MILVUS_PORT")
MILVUS_HOST=os.environ.get("MILVUS_HOST")
#COLLECTION_ARTICLE_NAME=str(os.environ.get("COLLECTION_ARTICLE_NAME"))
COLLECTION_RAPPORT_NAME=str(os.environ.get("COLLECTION_RAPPORT_NAME"))

COLLECTION_ARTICLE_INVESTIR_NAME=str(os.environ.get("COLLECTION_ARTICLE_INVESTIR_NAME"))
COLLECTION_ARTICLE_INDICATEUR_NAME=str(os.environ.get("COLLECTION_ARTICLE_INDICATEUR_NAME"))
COLLECTION_ARTICLE_TRANSACTION_NAME=str(os.environ.get("COLLECTION_ARTICLE_TRANSACTION_NAME"))

NB_ART=int(os.environ.get("NB_ART"))
VOISIN=int(os.environ.get("VOISIN"))
NB_RAPPORT=int(os.environ.get("NB_RAPPORT"))
URL_1024=os.environ.get("URL_1024")

connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)



index_params = {
    "metric_type": "IP",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024},
}

###########################################################################################""
#COLLECTION_ARTICLE = Collection(name=COLLECTION_ARTICLE_NAME)

#COLLECTION_ARTICLE.create_index("paragraphe_embedding", index_params)
#COLLECTION_ARTICLE.create_index("title_embedding", index_params)
#COLLECTION_ARTICLE.create_index("time_embedding", index_params)
#COLLECTION_ARTICLE.load()



###########################################################################################""
COLLECTION_ARTICLE_INVESTIR = Collection(name=COLLECTION_ARTICLE_INVESTIR_NAME)
COLLECTION_ARTICLE_INVESTIR.create_index("paragraphe_embedding", index_params)
COLLECTION_ARTICLE_INVESTIR.create_index("title_embedding", index_params)
COLLECTION_ARTICLE_INVESTIR.load()


########################################################################################################################
COLLECTION_RAPPORT = Collection(name=COLLECTION_RAPPORT_NAME)
COLLECTION_RAPPORT.create_index("paragraphe_embedding", index_params)
COLLECTION_RAPPORT.create_index("titre_embedding", index_params)
COLLECTION_RAPPORT.create_index("description_embedding", index_params)
COLLECTION_RAPPORT.create_index("dateparution_embedding", index_params)
COLLECTION_RAPPORT.load()


########################################################################################################################
COLLECTION_ARTICLE_INDICATEUR = Collection(name=COLLECTION_ARTICLE_INDICATEUR_NAME)
COLLECTION_ARTICLE_INDICATEUR.create_index("annee_embedding", index_params)
COLLECTION_ARTICLE_INDICATEUR.create_index("pays_embedding", index_params)
COLLECTION_ARTICLE_INDICATEUR.load()



########################################################################################################################
COLLECTION_ARTICLE_TRANSACTION = Collection(name=COLLECTION_ARTICLE_TRANSACTION_NAME)
COLLECTION_ARTICLE_TRANSACTION.create_index("description_embedding", index_params)
COLLECTION_ARTICLE_TRANSACTION.create_index("date_embedding", index_params)
COLLECTION_ARTICLE_TRANSACTION.create_index("row_embedding", index_params)
COLLECTION_ARTICLE_TRANSACTION.load()