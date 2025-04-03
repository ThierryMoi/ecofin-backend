from pymongo import MongoClient
from model.message_model import MessageBase, MessageRead, MessageResponse
from repository.message_repository import MessageRepository
from pymilvus import AnnSearchRequest, WeightedRanker
from utils.requests import embedding_multilangue
from utils.date_search import extract_year_with_context
from configuration.openai import CLIENT_OPENAI
from utils.requests import split_string_with_limit
from utils.prompts_search import template_system_search,human_prompt_search

from configuration.milvus import (
    NB_RAPPORT, NB_ART, COLLECTION_ARTICLE_INDICATEUR, COLLECTION_ARTICLE_TRANSACTION,
    COLLECTION_RAPPORT, URL_1024, VOISIN, COLLECTION_ARTICLE_INVESTIR ,COLLECTION_ARTICLE
)
#from configuration.milvus_dev import COLLECTION_ARTICLE_DEV

class MessageService:
    def __init__(self, message_repository,discussion_repository):
        self.repo = message_repository
        self.repo_discussion = discussion_repository

    def create_message(self, message: MessageBase) -> str:
        add= self.repo.create(message)
        msg = self.repo.nb_message_by_user_by_discussion(message.user_id, message.discussion_id)
        if msg is not None:    
            msg=str(msg)     
            #print(msg) 
            completion = CLIENT_OPENAI.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "tu es un spécialiste en redaction et résumé de  texte"},
                    {"role": "user", "content": f"resume cette discussion {msg}"}
                ]
            )
            resume = completion.choices[0].message.content

            completion = CLIENT_OPENAI.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "tu es un spécialiste en redaction et résumé de  texte"},
                    {"role": "user", "content": f"donne un titre de quelque mot à cette discussion {msg}"}
                ]
            )
            titre = completion.choices[0].message.content
            self.repo_discussion.update(message.discussion_id,{"name": titre,"resume":resume})
        return add


    def get_all_message_by_user_discussion(self, user_id, discussion_id, page, page_size) -> dict:
        lst, nb = self.repo.find_all_by_user_discussion(user_id, discussion_id, page, page_size)
        return {
            "message": lst,
            "page_size": page_size,
            "page": page,
            "nb_pages": nb
        }

    def get_message_by_id(self, message_id: str) -> MessageRead:
        return self.repo.find_by_id(message_id)

    def respond_to_message(self, message_id: str, response: str) -> bool:
        return self.repo.update_response(message_id, response)

    def config_search_request(self, field_name, vector, limit):
        return AnnSearchRequest(
            data=[vector],
            anns_field=field_name,
            param={
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            limit=limit
        )

    def config_multi_similar(self, vector, tmp_embed, fields, limit):
        return [self.config_search_request(field, vector if "date" not in field else tmp_embed, limit) for field in fields]

    def config_search_requests(self, vector, tmp_embed, collection):
        if collection == "rapport":
            return self.config_multi_similar(
                vector, tmp_embed, ["paragraphe_embedding", "titre_embedding", "description_embedding", "dateparution_embedding"], NB_RAPPORT
            )
        if collection == "article":
            return self.config_multi_similar(
                vector, tmp_embed, ["paragraphe_embedding", "title_embedding", "time_embedding"], NB_ART
            )
        if collection == "investir":
            return self.config_multi_similar(
                vector, tmp_embed, ["paragraphe_embedding", "title_embedding"], NB_ART
            )
        if collection == "indicateur":
            return self.config_multi_similar(
                vector, tmp_embed, ["annee_embedding", "pays_embedding"], NB_ART
            )
        if collection == "transaction":
            return self.config_multi_similar(
                vector, tmp_embed, ["description_embedding", "date_embedding", "row_embedding"], NB_ART
            )
        return []

    def list_partitions(self, collection):
        return [col.name for col in collection.partitions]

    def compute_freshness_score(self, date_field, reference_year):
        """
        Calcule un score de fraîcheur basé sur la proximité de la date avec l'année de référence.
        """
        if not date_field or not reference_year:
            return 0  # Aucun score si la date ou l'année de référence est manquante
        try:
            document_year = int(date_field)  # Extraire l'année du champ de date
            freshness = max(0, 1 - abs(document_year - int(reference_year)) / 10)  # Score décroissant au fil des années
            return freshness
        except ValueError:
            return 0  # Retourne 0 si le format de la date est invalide

    def combine_scores(self, relevance_score, freshness_score, alpha=0.7):
        """
        Combine le score de pertinence et de fraîcheur en utilisant une pondération alpha.
        """
        return alpha * relevance_score + (1 - alpha) * freshness_score

    def similar_documents(self, question, val, collection, output_fields, collection_obj, reranker_weights, limit, partition_by_year=None):
        entities = []
        lst_partition = []
        question_embed = eval(embedding_multilangue(question, URL_1024))
        tmp_embed = eval(embedding_multilangue(val, URL_1024))
        lst_partition_exists = self.list_partitions(collection_obj)

        # Sélection des partitions selon l'année
        if partition_by_year:
            if partition_by_year in lst_partition_exists:
                lst_partition = [partition_by_year]
            else:
                # Prendre les années proches ou toutes si aucune correspondance
                lst_partition = [
                    an for an in lst_partition_exists if an != "_default" and abs(int(an) - int(partition_by_year)) <= 2
                ] or lst_partition_exists
        else:
            lst_partition = lst_partition_exists

        # Configurer les requêtes
        reqs = self.config_search_requests(question_embed, tmp_embed, collection)
        rerank = WeightedRanker(*reranker_weights)

        # Recherche dans les partitions sélectionnées
        for partition in lst_partition:
            res = collection_obj.hybrid_search(
                reqs,
                rerank,
                limit=limit,
                output_fields=output_fields,
                partition_names=[partition]
            )
            # Ajouter des métadonnées pour le tri
            if len(res) > 0:
                for hit in res[0]:
                    distance = hit.distance
                    entity = hit.entity.to_dict()['entity']
                    date_field = entity.get("annee") 
                    freshness_score = self.compute_freshness_score(date_field, 2024)
                    combined_score = self.combine_scores(distance, freshness_score)
                    entities.append({"partition": partition, "combined_score": combined_score, "hit": entity})

        # Trier les entités par score combiné
        entities = sorted(entities, key=lambda x: x["combined_score"], reverse=True)
        return entities

    def rerank(self, COHERE_API_KEY, query, documents):
        from pymilvus.model.reranker import CohereRerankFunction

        cohere_rf = CohereRerankFunction(model_name="rerank-multilingual-v2.0", api_key=COHERE_API_KEY)
        results = cohere_rf(query=query, documents=documents, top_n=3)

        return [result.text for result in results]
 
    def consolidation_context(self, question, val, base):
        """
        Consolidation et classement des contextes pour différents types de bases de données.

        Args:
            question (str): La question posée.
            val (str): La valeur contextuelle à utiliser pour la recherche.
            base (list): Liste des types de bases à interroger.

        Returns:
            list: Contextes consolidés et classés pour chaque base.
        """
        consolidated_contexts = []
        year = extract_year_with_context(question)
        collection_mapping = {
            "article": {
                "collection": COLLECTION_ARTICLE,
                "output_fields": ["content", "numeros_paragraphe", "time_published", "pub_title", "authors","pub_link"],
                "weights": (0.4, 0.2, 0.4),
                "limit": NB_ART
            },
            "rapport": {
                "collection": COLLECTION_RAPPORT,
                "output_fields": ["content", "numeros_paragraphe", "dateparution", "titre", "description"],
                "weights": (0.5, 0.2, 0.2, 0.1),
                "limit": NB_RAPPORT
            },
            "investir_cameroun": {
                "collection": COLLECTION_ARTICLE_INVESTIR,
                "output_fields": ["content", "numeros_paragraphe", "pub_title", "authors","pub_link"],
                "weights": (0.6, 0.4),
                "limit": NB_ART
            },
            "indicateur": {
                "collection": COLLECTION_ARTICLE_INDICATEUR,
                "output_fields": [
                    "annee", "pays", "dhIndexRank", "pibUsd", "population", "pibPerHabitationUsd",
                    "externalDebtUsd", "inflation", "goodsAndServicesImportUsd", "goodsAndServicesExportUsd",
                    "foreignExchangeReserveUsd", "currentBalanceLocal", "exchangeRate", "currentBalanceUsd",
                    "transparencyIndexRank", "ecartIdhRnbHab", "monaieLocal"
                ],
                "weights": (0.5, 0.5),
                "limit": NB_ART
            }
        }

        question_embed = eval(embedding_multilangue(question, URL_1024))
        tmp_embed = eval(embedding_multilangue(val, URL_1024))

        for db_type in base:
            if db_type in collection_mapping:
                config = collection_mapping[db_type]
                results = self.similar_documents(
                    question=question,
                    val=val,
                    collection=db_type,
                    output_fields=config["output_fields"],
                    collection_obj=config["collection"],
                    reranker_weights=config["weights"],
                    limit=config["limit"],
                    partition_by_year=year
                )
                
                # Construire les contextes à partir des résultats
                formatted_results = []
                for result in results:
                    combined_score = result.get("combined_score", 0)
                    partition = result.get("partition", "N/A")
                    hit = result.get("hit", {})

                    # Formater le contenu à partir des champs définis
                    content = "\n".join([
                        f"{field.replace('_', ' ').capitalize()}: {hit.get(field, 'N/A')}"
                        for field in config["output_fields"] if field in hit
                    ])

                    formatted_results.append({
                        "partition": partition,
                        "score": combined_score,
                        "content": content
                    })

                # Trier les résultats par `combined_score` décroissant
                formatted_results.sort(key=lambda x: x["score"], reverse=True)
                # Ajouter les contenus triés au contexte consolidé
                consolidated_contexts.append({db_type: "\n\n".join([res["content"] for res in formatted_results])})
        return consolidated_contexts

    def recherche_consolider(self, question, val, base):
        """
        Consolidation et classement des contextes pour différents types de bases de données.

        Args:
            question (str): La question posée.
            val (str): La valeur contextuelle à utiliser pour la recherche.
            base (list): Liste des types de bases à interroger.

        Returns:
            list: Contextes consolidés et classés pour chaque base.
        """
        consolidated_contexts = []
        lst_doc=[]
        year = extract_year_with_context(question)
        collection_mapping = {
            "rapport": {
                "collection": COLLECTION_RAPPORT,
                "output_fields": [ "content", "dateparution", "titre", "description"],
                "weights": (0.5, 0.1, 0.1, 0.3),
                "limit": NB_RAPPORT
            },
            "indicateur": {
                "collection": COLLECTION_ARTICLE_INDICATEUR,
                "output_fields": [
                    "annee", "pays", "dhIndexRank", "pibUsd", "population", "pibPerHabitationUsd",
                    "externalDebtUsd", "inflation", "goodsAndServicesImportUsd", "goodsAndServicesExportUsd",
                    "foreignExchangeReserveUsd", "currentBalanceLocal", "exchangeRate", "currentBalanceUsd",
                    "transparencyIndexRank", "ecartIdhRnbHab", "monaieLocal"
                ],
                "weights": (0.5, 0.5),
                "limit": NB_ART
            }
        }

        question_embed = eval(embedding_multilangue(question, URL_1024))
        tmp_embed = eval(embedding_multilangue(val, URL_1024))
        
        formatted_results = []
        for db_type in base:
            if db_type in collection_mapping:
                config = collection_mapping[db_type]
                results = self.similar_documents(
                    question=question,
                    val=val,
                    collection=db_type,
                    output_fields=config["output_fields"],
                    collection_obj=config["collection"],
                    reranker_weights=config["weights"],
                    limit=config["limit"],
                    partition_by_year=year
                )
                
                # Construire les contextes à partir des résultats
                for result in results:
                    combined_score = result.get("combined_score", 0)
                    partition = result.get("partition", "N/A")
                    hit = result.get("hit", {})

                    content = {
                        field.capitalize(): hit.get(field, 'N/A')
                        for field in config["output_fields"]
                    }
                    contentchat = "\n".join([f"{field.replace('_', ' ').capitalize()}: {hit.get(field, 'N/A')}"
                        for field in config["output_fields"] if field in hit
                    ])
                    lst_doc.append(contentchat)
                    formatted_results.append({
                        "base_de_donnee": db_type,
                        "partition": partition,
                        "score": combined_score,
                        "content": content,
                        })

                    import tiktoken

        ENCODING = tiktoken.get_encoding("cl100k_base")
        

        completion = CLIENT_OPENAI.chat.completions.create(
                        model="gpt-4o",
                        temperature=0.8,
                        messages=[
                            {"role": "system", "content": template_system_search},
                            {
                                "role": "user",
                                "content": split_string_with_limit(human_prompt_search(question, lst_doc)
                                    ,
                                    20000,
                                    ENCODING
                                )
                            }                        ] 
                    )
        resume = completion.choices[0].message.content
        seen_titles = set()
        unique_results = []
        if db_type== "rapport":
            for result in formatted_results:
                del result["content"]["Content"]
                title = result["content"].get("Titre", "N/A")
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_results.append(result)

            formatted_results = unique_results

        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        return {"insight":resume,"sources":formatted_results}
