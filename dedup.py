# Perceptual hasing for Image deduplication
# Arthor = Tim Ng @ Sensetime HK

import os
import sys
from PIL import Image


def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)
    
def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

def similarity(dist):
    return (64 - dist) * 100 / 64

def dedup_imglist(prefix_folder, imglist, threshold = 97):
    # detect deduplication and return a list of deduped imglist
    num_img = len(imglist)
    assert(num_img>2)
    imglist = [prefix_folder + '/' + l for l in imglist]
    hashes = map(avhash,imglist)
    removed = [False] * num_img
    for i in range(num_img -1):
        for j in range(1,num_img):
            if not removed[i] and not removed[j] and i != j:
                dist = hamming(hashes[i], hashes[j])
                similar = similarity(dist)
                if similar > threshold:
                    removed[j] = True
                    #print j, "is removed by comparing", i, j
    imglist_dedup = [img for rm,img in zip(removed, imglist) if rm == False]
    return imglist_dedup


if __name__ == '__main__':
    folder = './data/'
    imglist = ['98a.jpg','98b.jpg','100a.jpg','100b.jpg']
    imglist_dedup = dedup_imglist(folder, imglist)
    print imglist_dedup



