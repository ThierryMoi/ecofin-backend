def generate_html_migration_fin(menom,meprenom, younom, youprenom, origine, residence):
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
    }

    .email-template {
        position: relative;
        width: 100%;
        min-height: 100vh;
        padding: 20px;
    }

    .email-template__container {
        max-width: 780px;
        margin: auto;
    }

    .email-template__header {
        background: linear-gradient(106deg, #fff 0%, #8c3ffb 68%);
        text-align: center;
        padding: 80px 20px;
    }

    .email-template__body {
        padding: 20px;
        font-size: 18px;
        margin-top: 50px;
    }

    .email-template__footer {
        padding: 20px;
        border-top: 1px solid #5118a2;
        margin-top: 50px;
        text-align: center;
    }

    .btn {
        cursor: pointer;
        background-color: #8c3ffb;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 15px;
        text-decoration: none;
    }

    .btn:hover {
        background-color: #5118a2;
    }

    .not-me {
        font-style: italic;
        font-size: 14px;
        margin: 30px 0;
    }

    .email-signature {
        margin-top: 30px;
    }

    .logo {
        width: 200px;
        height: 60px;
        background: url("https://res.cloudinary.com/dymyebgcf/image/upload/v1674563705/share/logo_dcu1if.png") center/cover no-repeat;
        margin: auto;
    }
    """

    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenue sur EDA</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>{css_styles}</style>
</head>
<body>
<div class="email-template">
    <div class="email-template__container">
        <header class="email-template__header email-template-header">
            <div class="email-template-header__text">
                <h1 style="font-size: 32px; margin-bottom: 10px;">EDA</h1>
                <span style="font-size: 18px;">Bonne Nouvelle! 😊</span>
            </div>
        </header>
        <div class="email-template__body">
            <p>Hello<strong> {meprenom} {menom}</strong>,</p>
            <p> <strong> {youprenom} {younom} venant de {residence} </strong> , vient d'arriver dans  votre communauté.! </p>
            <p>N'hesiter pas à lui souhaiter bonne arrivée et de l'aider dans son insertion . 🌍</p>
            <p>Conserver les liens peu importe la distance car vous venez tous de {origine} 🚀</p>
            <br>

            <p style="margin-top: 30px;">
                Cordialement,<br>
                L'équipe EDA
            </p>
        </div>
        <div class="email-template__footer">
            <div class="copyright">© 2024 EDA. Tous droits réservés.</div>
            <div class="logo"></div>
        </div>
    </div>
</div>
</body>
</html>
"""
    return html_template
