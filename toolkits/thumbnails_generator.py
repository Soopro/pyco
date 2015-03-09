import os
from PIL import Image

UPLOADS_DIR = 'uploads'
THUMBNAILS_DIR = 'thumbnails'
THUMBNAILS_H = 360
THUMBNAILS_W = 360


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
                im.thumbnail((w*THUMBNAILS_H/h, THUMBNAILS_H), Image.ANTIALIAS)
            else:
                im.thumbnail((THUMBNAILS_W, h*THUMBNAILS_W/w), Image.ANTIALIAS)
            if not os.path.exists(THUMBNAILS_DIR):
                os.makedirs(THUMBNAILS_DIR)
            im.save(os.path.join(THUMBNAILS_DIR, filename))
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