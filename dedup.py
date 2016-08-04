# Perceptual hasing for Image deduplication
# Arthor = Tim Ng @ Sensetime HK
import os
import sys
from PIL import Image
from multiprocessing import Pool, TimeoutError
import time

''' BK Tree '''
class BkTree:
     "A Bk-Tree implementation."
     def __init__(self, root, distance_function):
        self.df = distance_function
        self.root = root
        self.tree = (root, {})
     def build(self, words):
        "Build the tree."
        for word in words:
            self.tree = self.insert(self.tree, word)
     def insert(self, node, word):
        "Inserts a word in the tree."
        d = self.df(word[1], node[0][1])
        if d not in node[1]:
            node[1][d] = (word, {})
        else:
            self.insert(node[1][d], word)
        return node
     def query(self, word, max_dist):
        "Returns a list of words that have the specified edit distance from the search word."
        def search(node):
            d = self.df(word[1], node[0][1])
            results = []
            if d <= max_dist:
                results.append(node[0])
            for i in range(d-max_dist, d+max_dist+1):
                children = node[1]
                if i in children:
                    results.extend(search(node[1][i]))
            return results
        root = self.tree
        return search(root)


''' Perceptual hash '''
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

# def dedup_imglist(prefix_folder, imglist, threshold = 97):
#     # detect deduplication and return a list of deduped imglist
#     num_img = len(imglist)
#     assert(num_img>2)
#     imglist = [prefix_folder + '/' + l for l in imglist]
#     hashes = map(avhash,imglist)
#     removed = [False] * num_img
#     for i in range(num_img -1):
#         for j in range(1,num_img):
#             if not removed[i] and not removed[j] and i != j:
#                 dist = hamming(hashes[i], hashes[j])
#                 similar = similarity(dist)
#                 if similar > threshold:
#                     removed[j] = True
#                     #print j, "is removed by comparing", i, j
#     imglist_dedup = [img for rm,img in zip(removed, imglist) if rm == False]
#     return imglist_dedup


if __name__ == '__main__':
    folder = './data/'
    imglist = []
    for f in os.listdir(folder):
        if f.endswith('.jpg'):
            imglist.append(folder+'/'+f)

    # multithread compute hashing
    p = Pool(4)
    hashes = p.map(avhash, imglist)
    print 'All phash values: '
    for h in hashes:
        print "{0:b}".format(h)
    imgname_hash = zip(imglist, hashes)
    # print 'Image and its hash = ', imgname_hash

    # use the first node as the root, hamming distance as the distance
    bktree = BkTree(imgname_hash[0], hamming)
    # build the tree with remaining nodes
    bktree.build(imgname_hash[1:])

    # query a node ,e.g. imgname_hash[2]
    max_dist = 3 # at most 3 bits different
    print bktree.query(imgname_hash[4], max_dist)





