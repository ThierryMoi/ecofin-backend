from pymongo import MongoClient
from model.message_model import MessageBase, MessageRead, MessageResponse
from repository.message_repository import MessageRepository
from pymilvus import AnnSearchRequest,WeightedRanker
from utils.requests import embedding_multilangue
from configuration.milvus import NB_RAPPORT, NB_ART, COLLECTION_RAPPORT, COLLECTION_ARTICLE,URL_1024,VOISIN

class MessageService:
    def __init__(self,message_repository):
        self.repo =message_repository

    def create_message(self, message: MessageBase) -> str:
        return self.repo.create(message)

    def get_all_message_by_user_discussion(self,user_id ,discussion_id,page,page_size) -> dict:
        dc={}
        lst , nb = self.repo.find_all_by_user_discussion(user_id, discussion_id, page,page_size)
        dc["message"]=lst
        dc["page_size"]=page_size
        dc["page"]=page
        dc["nb_pages"]=nb
        print(dc)
        return dc
        
 

    def get_message_by_id(self, message_id: str) -> MessageRead:
        return self.repo.find_by_id(message_id)

    def respond_to_message(self, message_id: str, response: str) -> bool:
        return self.repo.update_response(message_id, response)
    

    def config_multi_simarl_rapport(self,vector):
        search_param_1 = {
            "data": [vector],
            "anns_field": "paragraphe_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_RAPPORT
        }
        request_1 = AnnSearchRequest(**search_param_1)

        search_param_2 = {
            "data": [vector],
            "anns_field": "titre_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_RAPPORT
        }
        request_2 = AnnSearchRequest(**search_param_2)



        search_param_3 = {
            "data": [vector],
            "anns_field": "description_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_RAPPORT
        }
        request_3 = AnnSearchRequest(**search_param_3)
        search_param_4 = {
            "data": [vector],
            "anns_field": "dateparution_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_RAPPORT
        }
        request_4 = AnnSearchRequest(**search_param_4)

        return [request_1, request_2,request_3,request_4]


    
    def config_multi_simarl_article(self,vector):
        search_param_1 = {
            "data": [vector],
            "anns_field": "paragraphe_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_ART
        }
        request_1 = AnnSearchRequest(**search_param_1)

        search_param_2 = {
            "data": [vector],
            "anns_field": "title_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_ART
        }
        request_2 = AnnSearchRequest(**search_param_2)



        search_param_3 = {
            "data": [vector],
            "anns_field": "time_embedding",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": VOISIN}
            },
            "limit": NB_ART
        }
        request_3 = AnnSearchRequest(**search_param_3)

        return [request_1, request_2,request_3]

    

    def similar_articles(self, question: str):
        entities = []
        question_embed= eval(embedding_multilangue(question,URL_1024))
        reqs = self.config_multi_simarl_article(question_embed)
        rerank = WeightedRanker(0.7,0.2, 0.1)
        res = COLLECTION_ARTICLE.hybrid_search(
            reqs,
            rerank,
            limit=NB_ART ,
            output_fields=["content","numeros_paragraphe","time_published","pub_title","authors"],

        )
        for hit in res[0]:
            entities.append(hit.entity.to_dict()['entity'])
        return entities

    def similar_rapport(self, question: str):
        entities=[]
        question_embed= eval(embedding_multilangue(question,URL_1024))
        reqs = self.config_multi_simarl_rapport(question_embed)
        rerank = WeightedRanker(0.5, 0.2, 0.2, 0.1)
        res = COLLECTION_RAPPORT.hybrid_search(
            reqs,
            rerank,
            limit=NB_RAPPORT ,
            output_fields=["content","numeros_paragraphe","description","titre","dateparution"],

        )
        for hit in res[0]:
            entities.append(hit.entity.to_dict()['entity'])
        return entities    
    
    
    def consolidation_context(self,question):
        context_article = self.similar_articles(question)
        context_rapport = self.similar_rapport(question)
        rapport_str = "\n\n".join([
        f"{'content chunk article: ' + article['content']}\n"
        f"{'numeros du chunck: ' + article['numeros_paragraphe']}\n"
        f"{'periode du context du rapport: ' + article['dateparution']}\n"
        f"{'titre du rapport: ' + article['titre']}\n"
        f"{'description:' + article['description']}\n\n"
        for index, article in enumerate(context_rapport)])

        article_str = "\n\n".join([
        f"{'content chunk : ' + article['content']}\n"
        f"{'numeros du paragraphe: ' + article['numeros_paragraphe']}\n"
        f"{'periode du context: ' + article['time_published']}\n"
        f"{'titre de larticle: ' + article['pub_title']}\n"
        f"{'authors:' + article['authors']}\n\n"
        for index, article in enumerate(context_article)])
        
        return article_str, rapport_str
        
        




        