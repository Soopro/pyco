import os
from PIL import Image

UPLOADS_DIR = 'uploads'
THUMBNAIL_DIR = 'thumbnail'
THUMBNAIL_H = 480
THUMBNAIL_W = 480


def generate_thumbnail(filename):
    # get file type from filename

    file_type = os.path.splitext(filename)[1][1:].upper()

    thumbnail_format = {
        'JPG': 'JPEG',
        'JPEG': 'JPEG',
        'PNG': 'PNG',
        'GIF': 'GIF'
    }
    format_type = thumbnail_format.get(file_type)
    if format_type:
        try:
            im = Image.open(filename)
            w, h = im.size
            if w < h:
                im.thumbnail((w*THUMBNAIL_H/h, THUMBNAIL_H), Image.ANTIALIAS)
            else:
                im.thumbnail((THUMBNAIL_W, h*THUMBNAIL_W/w), Image.ANTIALIAS)
            if not os.path.exists(THUMBNAIL_DIR):
                os.makedirs(THUMBNAIL_DIR)
            im.save(os.path.join(THUMBNAIL_DIR, filename))
        except IOError as e:
            raise e
    else:
        print filename


def walkfiles(source):
    print '== illegal files =='
    for f in os.listdir(source):
        if os.path.isfile(f):
            generate_thumbnail(f)
    print "== done =="

if __name__ == '__main__':
    os.chdir(os.path.join('..', UPLOADS_DIR))
    walkfiles('.')