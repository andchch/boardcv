from shiftlab_ocr.doc2text.reader import Reader


def recognize_text(img: str):
    reader = Reader()
    result = reader.doc2text(img)
    
    return result[0]