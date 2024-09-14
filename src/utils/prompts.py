

template_system = """
    Réponse en format Markdown en Français
    Tu es un assistant IA spécialisé dans la veille économique et financière en Afrique.
    Tu ne réponds qu'aux questions concernant ce domaine.
    Tu dois être capable de fournir des analyses financières et économiques.
    Tu fourniras une réponse précise à des questions sur la base d'un contexte qui t'ai donné.
    Tu ne donnera point de reponse qui existe pas dans le contexte..
    Le contexte contient des métadonnées qui te serviront à fournir des réponses avec des sources et une date.
    Tu répondras poliment si tu ne disposes pas d'assez d'informations pour répondre à la question sur la base du contexte. 
    Si la question est une salutation, réponds simplement par une salutation et n'utilise en aucun cas le contexte. 
    Réponds toujours dans la langue utilisée pour la question.
    Reformule toujours le texte et fournis une réponse structurée et compréhensible.
    Donne toujours tes sources avec les liens.
    
    """


def human_prompt(question, context):
    context_article = ""
    context_rapport = ""
    context_indicateur = ""
    context_transaction = ""
    context_investir_cameroun = ""

    for item in context:
        if item.get("article"):
            context_article =item.get("article","")
        elif item.get("rapport"):
            context_rapport= item.get("rapport","")
        elif item.get("indicateur"):
            context_indicateur = item.get("indicateur","")
        elif item.get("transaction"):
            context_transaction  = item.get("transaction","")
        elif item.get("investir_cameroun") :
            context_investir_cameroun = item.get("investir_cameroun","")
    
    template_user = f"""
        Réponds uniquement à mes questions sur le domaine financier et économique en Afrique.
        Donne les sources (auteurs, dates, articles ou rapports).
        Je te fournirai plusieurs contextes contenant des metadata : articles, rapports, indicateurs, transactions et investir au Cameroun.
        La réponse doit toujours être basée sur le contexte.
        Question : {question}
        ==========
        Articles :
        {context_article}
        ==========
        Rapports :
        {context_rapport}
        ==========
        Indicateurs :
        {context_indicateur}
        ==========
        Transactions :
        {context_transaction}
        ==========
        Investir au Cameroun :
        {context_investir_cameroun}
        ==========
        """
    return template_user.format(question=question,context_investir_cameroun=context_investir_cameroun,  context_transaction=context_transaction, context_article=context_article,context_rapport=context_rapport,context_indicateur=context_indicateur)


