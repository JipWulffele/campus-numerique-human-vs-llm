from gensim.models import KeyedVectors

model_en = KeyedVectors.load_word2vec_format("wiki.en.align.vec")
model_en.save("wiki.multi.en.kv")

model_fr = KeyedVectors.load_word2vec_format("wiki.fr.align.vec")
model_fr.save("wiki.multi.fr.kv")