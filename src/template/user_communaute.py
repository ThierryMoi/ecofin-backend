def generate_html_new_member(receiver_name, new_member_name):
    css_styles = """
    /* Ton code CSS ici */
    /* styles.css */

    *,
    *::after,
    *::before {
        padding: 0;
        margin: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Montserrat', sans-serif;
        background-color: #ecebff;
        color: #000;
        text-align: center;
    }

    .container {
        max-width: 600px;
        margin: auto;
        padding: 20px;
    }

    .header {
        background: linear-gradient(106deg, #fff 0%, #8c3ffb 68%);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .header h1 {
        font-size: 32px;
        margin-bottom: 10px;
    }

    .header p {
        font-size: 18px;
    }

    .body {
        padding: 20px;
        border-radius: 8px;
        background-color: #fff;
        margin-bottom: 20px;
    }

    .body p {
        font-size: 18px;
        margin-bottom: 20px;
    }

    .footer {
        background-color: #8c3ffb;
        padding: 20px;
        border-radius: 8px;
        color: #fff;
    }

    .footer p {
        font-size: 18px;
        margin-bottom: 20px;
    }

    .footer a {
        color: #fff;
        text-decoration: none;
        font-weight: bold;
    }

    .footer a:hover {
        text-decoration: underline;
    }
    """

    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelle arrivée dans la communauté</title>
    <style>{css_styles}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Expertise Diaspora Africaine</h1>
            <p>Nous avons le plaisir de vous informer qu'un nouveau membre vient de nous rejoindre.</p>
        </div>
        <div class="body">
            <p>Cher {receiver_name},</p>
            <p>Nous sommes heureux de vous annoncer que {new_member_name} vient de rejoindre votre communauté.</p>
            <p>Si vous souhaitez prendre contact avec lui et lui souhaiter la bienvenue, n'hésitez pas à lui envoyer un message :</p>
   
        </div>
        <div class="footer">
            <p>N'hésitez pas à <a href="#">contacter notre équipe</a> si vous avez des questions ou des suggestions.</p>
        </div>
    </div>
</body>
</html>
"""
    return html_template

