import os
import re

t="""/*
Title: %s
Date: 2014/11/17
Author: DevinPan
Location: Shanghai
Template: works
Type: works
Alias:%s
Thumbnail: /uploads/%s
Description: Turnix Multimedia Studio
Order:1
*/
I know you think that I shouldn't still love you,
Or tell you that.
But if I didn't say it, well I'd still have felt it
where's the sense in that?
"""
INPUT_DIR = 'uploads'
OUTPUT_DIR = 'content'


def clean_filename(file):
    r = re.compile(r'[A-Za-z\.\d_\-/]')
    newfilename = ''.join(re.findall(r, file)).replace('-', '_').lower()
    os.rename(file, newfilename)
    return newfilename


def gen(file):
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    file = clean_filename(file)
    filename_with_ext = file.split('/')[-1]
    filename = filename_with_ext.split('.')[0]
    f = open(os.path.join(OUTPUT_DIR, filename+'.md'), 'w')
    f.write(t % (filename, filename, filename_with_ext))
    f.close()
    print file


def walkfiles(source):
    for dirpath, dirnames, filenames in os.walk(source):
        for file in filenames:
            gen(os.path.join(dirpath, file))


if __name__ == '__main__':
    walkfiles(INPUT_DIR)