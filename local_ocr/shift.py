import urllib

from shiftlab_ocr.doc2text.reader import Reader

reader = Reader()
result = reader.doc2text('pred/photo01.jpg')
print(result[0])
