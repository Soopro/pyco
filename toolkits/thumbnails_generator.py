import os

UPLOADS_DIR = 'uploads'

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
            im = Image.open(os.path.join(UPLOADS_DIR, filename))
            w, h = im.size
            im.thumbnail((w*THUMBNAILS_H/h, THUMBNAILS_H), Image.ANTIALIAS)
            thumbnail_folder = _thumbnail_path(app_alias)
            if not os.path.exists(thumbnail_folder):
                os.makedirs(thumbnail_folder)
            im.save(os.path.join(_thumbnail_path(app_alias), filename))
        except IOError as e:
            raise e
    else:
        raise ValueError('generate thumbnail failed: unknown file type.')


def walkfiles(source):
    for dirpath, dirnames, filenames in os.walk(source):
        for file in filenames:
            generate_thumbnail(file)


if __name__ == '__main__':
    walkfiles(UPLOADS_DIR)