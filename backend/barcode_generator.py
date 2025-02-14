import random
import string

def generate_barcode():
    """Generates a random 8-character barcode"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
