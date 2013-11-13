# -*- encoding: utf-8 -*-
import math

import nltk
import numpy

import Aot


class TextTools:
    def __init__(self, doc_id_to_text):
        self.docs = doc_id_to_text
        self.doc_infos_list = [Aot.get_lemma_infos(doc_text) for doc_text in self.docs.values()]
        self.doc_lemmas_list = [[info.normal_form for info in doc_infos] for doc_infos in self.doc_infos_list]

        norm_docs = [" ".join(lemmas) for lemmas in self.doc_lemmas_list]
        self.text_collection = nltk.TextCollection(norm_docs)
        self.unicode_stopwords = set([w.decode("utf-8") for w in nltk.corpus.stopwords.words('russian')])

    def pos_tagged_collocations(self, pos_template_list):
        collocations = {template: [] for template in pos_template_list}
        for word_infos in self.doc_infos_list:
            for i in xrange(len(word_infos) - 1):
                if word_infos[i] is None or word_infos[i + 1] is None:
                    continue
                pos_pair = Aot.get_pos_tag(word_infos[i]), Aot.get_pos_tag(word_infos[i + 1])
                if pos_pair in collocations.keys():
                    collocations[pos_pair].append((word_infos[i].normal_form, word_infos[i + 1].normal_form))
        return collocations

    def get_terms(self):
        terms = []
        [terms.extend(lemmas) for lemmas in self.doc_lemmas_list]
        return terms

    def idf(self, word):
        return self.text_collection.idf(word)

    def get_all_lemma_tuples(self, n):
        pairs = []
        for doc_lemmas in self.doc_lemmas_list:
            words = [lemma for lemma in doc_lemmas if
                     lemma not in self.unicode_stopwords]
            for i in xrange(len(words) - n + 1):
                pairs.append(tuple(words[i:i + n]))
        return pairs

    @staticmethod
    def collocation_word_index(collocations):
        word_index = {}
        for col in collocations.keys():
            if col[0] not in word_index:
                word_index[col[0]] = 0
            if col[1] not in word_index:
                word_index[col[1]] = 0
            word_index[col[0]] += collocations[col]
            word_index[col[1]] += collocations[col]
        return word_index

    @staticmethod
    def get_chi2_collocations_list(collocations):
        collocations = nltk.FreqDist(collocations)
        chi2_collocations = {}
        all_cols = sum(collocations.values())
        word_index = TextTools.collocation_word_index(collocations)
        for col in collocations.keys():
            this_col = collocations[col]
            w1_cols = word_index[col[0]] - this_col
            w2_cols = word_index[col[1]] - this_col
            other_cols = (all_cols - w1_cols - w2_cols - this_col)

            nom = all_cols * ((this_col * other_cols - w1_cols * w2_cols) ** 2)
            den = (this_col + w1_cols) * (this_col + w2_cols) * (other_cols + w1_cols) * (other_cols + w2_cols)
            chi2_collocations[col] = float(nom) / den
        return sorted(chi2_collocations.items(), key=lambda x: x[1], reverse=True)

    def get_coentry_terms(self, filter_fun=lambda x: True):
        terms = {}
        for doc_lemmas in self.doc_lemmas_list:
            is_valid = lambda w: w not in self.unicode_stopwords and filter_fun(w)
            words = list(set(lemma for lemma in doc_lemmas if is_valid(lemma)))
            for i in xrange(len(words)):
                for j in xrange(i, len(words)):
                    pair = tuple(sorted((words[i], words[j])))
                    if pair not in terms:
                        terms[pair] = 0
                    terms[pair] += 1
        return terms

    def _get_vector(self, term_to_id, pair_to_freq_list):
        vector = [0] * len(term_to_id)
        for pair in pair_to_freq_list:
            for term in pair[0]:
                vector[term_to_id[term]] += pair[1]
        return vector

    def get_coentry_word_matrix(self, coentry_terms):
        term_to_id = {}
        for item in coentry_terms.items():
            for term in item[0]:
                if term not in term_to_id:
                    term_to_id[term] = len(term_to_id)
        matrix = {term: [0] * len(term_to_id) for term in term_to_id.keys()}
        for item in coentry_terms.items():
            t1, t2 = item[0]
            matrix[t1][term_to_id[t2]] += item[1]
            matrix[t2][term_to_id[t1]] += item[1]
        return matrix

    def cos_sim(self, vector1, vector2):
        norm1 = numpy.linalg.norm(vector1)
        norm2 = numpy.linalg.norm(vector2)
        if norm1 - 0.0 < 0.0000001 or norm2 - 0.0 < 0.0000001:
            return 0.0
        return float(numpy.dot(vector1, vector2)) / (norm1 * norm2)

    def get_cosine_terms(self, term_to_vector_dict):
        terms = list(term_to_vector_dict.keys())
        pair_to_scalar_product = {}
        for i in xrange(len(terms) - 1):
            for j in xrange(i + 1, len(terms)):
                cos_sim = self.cos_sim(term_to_vector_dict[terms[i]], term_to_vector_dict[terms[j]])
                pair_to_scalar_product[(terms[i], terms[j])] = cos_sim
            print("\t" + str(i) + "-th term done!")
        del term_to_vector_dict
        del terms
        return pair_to_scalar_product

    @staticmethod
    def _fill_dict_by_lemmas(distances, lemmas):
        for i in xrange(len(lemmas)):
            for j in xrange(i, len(lemmas)):
                if lemmas[i] not in distances:
                    distances[lemmas[i]] = {}
                if lemmas[j] not in distances[lemmas[i]]:
                    distances[lemmas[i]][lemmas[j]] = []
                distances[lemmas[i]][lemmas[j]].append(j - i)

    def dist_matrix(self):
        distances = {}
        for lemmas in self.doc_lemmas_list:
            self._fill_dict_by_lemmas(distances, lemmas)
        terms = distances.keys()
        for w1 in distances.keys():
            for w2 in distances[w1].keys():
                distances[w1][w2] = numpy.mean(distances[w1][w2])
            distances[w1] = [distances[w1][term] if term in distances[w1] else 0.0 for term in terms]
        return distances

    def frequent_collocations(self, pos_template_list):
        collocations = self.pos_tagged_collocations(pos_template_list)
        return {template: sorted(nltk.FreqDist(collocations[template]).items(), key=lambda x: x[1], reverse=True)
                for template in collocations.keys()}

    def get_stable_collocations(self, pos_template_list):
        triples_dist = nltk.FreqDist(self.get_all_lemma_tuples(3))
        pos_collocations = self.frequent_collocations(pos_template_list)
        return {pos: self.get_stable_pairs(pos_collocations[pos], triples_dist) for pos in pos_collocations.keys()}

    @staticmethod
    def get_stable_pairs(freq_collocations, triples_dist):
        first_pair_triples = {}
        second_pair_triples = {}
        for triple in triples_dist.keys():
            if (triple[0], triple[1]) not in first_pair_triples:
                first_pair_triples[(triple[0], triple[1])] = 0
            first_pair_triples[(triple[0], triple[1])] += triples_dist[triple]
            if (triple[1], triple[2]) not in second_pair_triples:
                second_pair_triples[(triple[1], triple[2])] = 0
            second_pair_triples[(triple[1], triple[2])] += triples_dist[triple]

        stable = []
        for item in freq_collocations:
            col = item[0]
            is_stable_left = col in second_pair_triples and item[1] / second_pair_triples[col] < 2
            is_stable_right = col in first_pair_triples and item[1] / first_pair_triples[col] < 2
            if is_stable_left and is_stable_right:
                stable.append(item)
        return stable

    
    


