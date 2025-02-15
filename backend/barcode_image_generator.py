import os
from barcode import Code128
from barcode.writer import ImageWriter

BARCODE_FOLDER = "../barcodes/"
os.makedirs(BARCODE_FOLDER, exist_ok=True)

def generate_barcode_image(barcode_number, output_path):
    """
    Generates a barcode image for the given barcode number.
    """
    barcode = Code128(str(barcode_number), writer=ImageWriter())
    barcode.save(output_path)
