import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuração base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pasta de dados de aventuras
    QUESTS_FOLDER = os.path.join(basedir, 'app', 'data', 'quests')

    # Configurações de idioma
    BABEL_DEFAULT_LOCALE = 'pt_PT'
