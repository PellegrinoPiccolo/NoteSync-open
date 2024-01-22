import re

def is_valid_password(password):
    # Verifica se la password ha almeno 8 caratteri
    if len(password) < 8:
        return False

    # Verifica se la password contiene almeno una lettera minuscola
    if not any(char.islower() for char in password):
        return False

    # Verifica se la password contiene almeno una lettera maiuscola
    if not any(char.isupper() for char in password):
        return False

    # Verifica se la password contiene almeno un numero
    if not any(char.isdigit() for char in password):
        return False

    # Verifica se la password contiene almeno un carattere speciale
    special_chars = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if not special_chars.search(password):
        return False

    # La password ha superato tutti i controlli
    return True


def is_valid_email(email):
    # Espressione regolare per convalidare l'email
    email_regex = re.compile(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$')

    # Convalida l'email utilizzando l'espressione regolare
    return bool(re.match(email_regex, email))
