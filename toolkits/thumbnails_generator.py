import os
from PIL import Image

UPLOADS_DIR = 'uploads'
THUMBNAILS_DIR = 'thumbnails'
THUMBNAILS_H = 360
THUMBNAILS_W = 360


def generate_thumbnail(dirpath, filename):
    file = os.path.join(dirpath, filename)
    print file
    if not os.path.isfile(file):
        return
    # get file type from filename
    file_type = os.path.splitext(filename)[1][1:].upper()
    print file
    thumbnail_format = {
        'JPG': 'JPEG',
        'JPEG': 'JPEG',
        'PNG': 'PNG',
        'GIF': 'GIF'
    }
    format_type = thumbnail_format.get(file_type)

    if format_type:
        try:
            im = Image.open(file)
            w, h = im.size
            if w < h:
                im.thumbnail((w*THUMBNAILS_H/h, THUMBNAILS_H), Image.ANTIALIAS)
            else:
                im.thumbnail((THUMBNAILS_W, h*THUMBNAILS_W/w), Image.ANTIALIAS)
            if not os.path.exists(os.path.join(THUMBNAILS_DIR, dirpath)):
                os.makedirs(os.path.join(THUMBNAILS_DIR, dirpath))
            im.save(os.path.join(THUMBNAILS_DIR, file))
        except IOError as e:
            raise e
    else:
        raise ValueError('generate thumbnail failed: unknown file type.')


def walkfiles(source):
    for dirpath, dirnames, filenames in os.walk(source):
        for filename in filenames:
            generate_thumbnail(dirpath, filename)

if __name__ == '__main__':
    os.chdir('..')
    walkfiles(UPLOADS_DIR)