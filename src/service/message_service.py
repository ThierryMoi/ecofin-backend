from pymongo import MongoClient
from model.message_model import MessageBase, MessageRead, MessageResponse
from repository.message_repository import MessageRepository
from pymilvus import AnnSearchRequest, WeightedRanker
from utils.requests import embedding_multilangue
from utils.date_search import extract_year_with_context

from configuration.milvus import (
    NB_RAPPORT, NB_ART, COLLECTION_ARTICLE_INDICATEUR, COLLECTION_ARTICLE_TRANSACTION,
    COLLECTION_RAPPORT, URL_1024, VOISIN, COLLECTION_ARTICLE_INVESTIR
)
from configuration.milvus_dev import COLLECTION_ARTICLE_DEV

class MessageService:
    def __init__(self, message_repository):
        self.repo = message_repository

    def create_message(self, message: MessageBase) -> str:
        return self.repo.create(message)

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

    def similar_documents(self, question, val, collection, output_fields, collection_obj, reranker_weights, limit, partition_by_year=None):
        entities = []
        lst_partition = []
        question_embed = eval(embedding_multilangue(question, URL_1024))
        tmp_embed = eval(embedding_multilangue(val, URL_1024))
        lst_partition_exists = self.list_partitions(collection_obj)
        if partition_by_year:
            if partition_by_year in lst_partition_exists:
                lst_partition = [partition_by_year] 
            else:
                for an in lst_partition_exists:
                   if int(an) - int(partition_by_year) in [-1,-2,2, 1]:
                        lst_partition.append(an)
                   else:
                        lst_partition = lst_partition_exists
        else :
            lst_partition= lst_partition_exists
        reqs = self.config_search_requests(question_embed, tmp_embed, collection)
        rerank = WeightedRanker(*reranker_weights)

        for partition in lst_partition:
            res = collection_obj.hybrid_search(
                reqs,
                rerank,
                limit=limit,
                output_fields=output_fields,
                partition_names=[partition]
            )
            for hit in res[0][:3]:
                entities.append({"partition": partition, "distance": hit.distance, "hit": hit.entity.to_dict()['entity']})
                #print(hit.entity.to_dict())
        return entities

    def rerank(self, COHERE_API_KEY, query, documents):
        from pymilvus.model.reranker import CohereRerankFunction

        cohere_rf = CohereRerankFunction(model_name="rerank-multilingual-v2.0", api_key=COHERE_API_KEY)
        results = cohere_rf(query=query, documents=documents, top_n=3)

        return [result.text for result in results]

    def consolidation_context(self, question, val, base):
        consolidated_contexts = []
        annee= extract_year_with_context(question)            
        if "article" in base:
            art=self.similar_documents(
                question, val, "article", ["content", "numeros_paragraphe", "time_published", "pub_title", "authors"],
                COLLECTION_ARTICLE_DEV, (0.4, 0.2, 0.4), NB_ART,annee
            )
            list_art=[
            f"{'content chunk : ' + article['hit']['content']}\n"
            f"{'numeros du paragraphe: ' + article['hit']['numeros_paragraphe']}\n"
            f"{'periode du context: ' + article['hit']['time_published']}\n"
            f"{'titre de larticle: ' + article['hit']['pub_title']}\n"
            f"{'authors:' + article['hit']['authors']}\n\n"
            for index, article in enumerate(art)]
            consolidated_contexts.append({"article":"\n\n".join(list_art)})
                        
      
        if "rapport" in base:
            rap=self.similar_documents(
                question, val, "rapport", ["content", "numeros_paragraphe", "dateparution", "titre", "description"],
                COLLECTION_RAPPORT, (0.5, 0.2, 0.2, 0.1), NB_RAPPORT,annee
            )
            list_rap=[
            f"{'content chunk article: ' + article['hit']['content']}\n"
            f"{'numeros du chunck: ' + article['hit']['numeros_paragraphe']}\n"
            f"{'periode du context du rapport: ' + article['hit']['dateparution']}\n"
            f"{'titre du rapport: ' + article['hit']['titre']}\n"
            f"{'description:' + article['hit']['description']}\n\n"
            for index, article in enumerate(rap)]
            consolidated_contexts.append({"rapport":"\n\n".join(list_rap)})
            

        if "investir_cameroun" in base:
            rap = self.similar_documents(
                question, val, "investir", ["content", "numeros_paragraphe", "pub_title", "authors"],
                COLLECTION_ARTICLE_INVESTIR, (0.6, 0.4), NB_ART,annee
            )
            list_rap = [
                f"{'contenu: ' + article['hit']['content']}\n"
                f"{'numéros de paragraphe: ' + article['hit']['numeros_paragraphe']}\n"
                f"{'titre de la publication: ' + article['hit']['pub_title']}\n"
                f"{'auteurs: ' + article['hit']['authors']}\n\n"
                for index, article in enumerate(rap)
            ]
            consolidated_contexts.append({"investir_cameroun":"\n\n".join(list_rap)})

       
        if "indicateur" in base:
            rap = self.similar_documents(
                question, val, "indicateur", [
                    "annee", "pays", "dhIndexRank", "pibUsd", "population", "pibPerHabitationUsd", "externalDebtUsd", 
                    "inflation", "goodsAndServicesImportUsd", "goodsAndServicesExportUsd","foreignExchangeReserveUsd","currentBalanceLocal",
                    "exchangeRate","currentBalanceUsd","transparencyIndexRank","ecartIdhRnbHab","monaieLocal"
                ],
                COLLECTION_ARTICLE_INDICATEUR, (0.5, 0.5), NB_ART,annee
            )
            list_rap = [
                f"{'année: ' + article['hit']['annee']}\n"
                f"{'pays: ' + article['hit']['pays']}\n"
                f"{'classement de lindice DH: ' + article['hit']['dhIndexRank']}\n"
                f"{'PIB (USD): ' + article['hit']['pibUsd']}\n"
                f"{'population: ' + article['hit']['population']}\n"
                f"{'PIB par habitant (USD): ' + article['hit']['pibPerHabitationUsd']}\n"
                f"{'dette extérieure (USD): ' + article['hit']['externalDebtUsd']}\n"
                f"{'inflation: ' + article['hit']['inflation']}\n"
                f"{'importations de biens et services (USD): ' + article['hit']['goodsAndServicesImportUsd']}\n"
                f"{'exportations de biens et services (USD): ' + article['hit']['goodsAndServicesExportUsd']}\n"
                f"{'réserve de change (USD): ' + article['hit']['foreignExchangeReserveUsd']}\n"
                f"{'solde courant local: ' + article['hit']['currentBalanceLocal']}\n"
                f"{'taux de change: ' + article['hit']['exchangeRate']}\n"
                f"{'solde courant (USD): ' + article['hit']['currentBalanceUsd']}\n"
                f"{'classement de lindice de transparence: ' + article['hit']['transparencyIndexRank']}\n"
                f"{'écart IDH/RNB par habitant: ' + article['hit']['ecartIdhRnbHab']}\n"
                f"{'monnaie locale: ' + article['hit']['monaieLocal']}\n\n"
                for index, article in enumerate(rap)
            ]
            consolidated_contexts.append({"indicateur":"\n\n".join(list_rap)})



        if "transaction" in base:
            rap = self.similar_documents(
                question, val, "transaction", [
                    "typeTransaction", "date", "natureTransaction", "secteursTransaction", "description", 
                    "investisseurs", "beneficiares", "paysInvestisseurs", "paysBeneficiares", "valeurTotal", 
                    "nombreBeneficaire"
                ],
                COLLECTION_ARTICLE_TRANSACTION, (0.4, 0.2, 0.4), NB_ART,annee
            )
            list_rap = [
                f"{'type de transaction: ' + article['hit']['typeTransaction']}\n"
                f"{'date: ' + article['hit']['date']}\n"
                f"{'nature de la transaction: ' + article['hit']['natureTransaction']}\n"
                f"{'secteurs de la transaction: ' + article['hit']['secteursTransaction']}\n"
                f"{'description: ' + article['hit']['description']}\n"
                f"{'investisseurs: ' + article['hit']['investisseurs']}\n"
                f"{'bénéficiaires: ' + article['hit']['beneficiares']}\n"
                f"{'pays des investisseurs: ' + article['hit']['paysInvestisseurs']}\n"
                f"{'pays des bénéficiaires: ' + article['hit']['paysBeneficiares']}\n"
                f"{'valeur totale: ' + article['hit']['valeurTotal']}\n"
                f"{'nombre de bénéficiaires: ' + article['hit']['nombreBeneficaire']}\n\n"
                for index, article in enumerate(rap)
            ]
            consolidated_contexts.append({"transaction":"\n\n".join(list_rap)})
            
        return consolidated_contexts
