from TextTools import TextTools
import nltk
import codecs
import os


class TextToolsOutput:
    def __init__(self, doc_id_to_text, dir_to_save_results):
        self.dir_to_save = dir_to_save_results
        self.tools = TextTools(doc_id_to_text)

        self.coentry_terms_file_name = "cooccurent_terms.txt"
        self.chi2_all_file_name = 'chi2_all.txt'
        self.stable_terms_file_name = "stable_collocations.txt"
        self.scalar_product_terms_file_name = "cos_product_terms.txt"
        self.dist_terms_file_name = "dist_terms.txt"
        self.idf_distrib_file_name = "idf_distrib.txt"

    def frequent_collocations(self, pos_template_list):
        pos_collocations = self.tools.frequent_collocations(pos_template_list)
        for template in pos_collocations.keys():
            file_name = os.path.join(self.dir_to_save, 'freq_' + template[0] + '_' + template[1] + '.txt')
            with codecs.open(file_name, 'w', 'utf-8') as f:
                for item in pos_collocations[template]:
                    col = item[0]
                    freq = item[1]
                    freq_part = col[0] + ' ' + col[1] + '\t' + str(freq)
                    idf_part = str(self.tools.idf(col[0])) + "\t" + str(self.tools.idf(col[1]))
                    f.write(freq_part + "\t" + idf_part + '\n')

    def chi2_collocations(self, pos_template_list=None):
        if pos_template_list is None:
            return self._save_chi2_collocations(self.tools.get_all_lemma_tuples(2), self.chi2_all_file_name)
        collocations = self.tools.pos_tagged_collocations(pos_template_list)
        for template in collocations.keys():
            self._save_chi2_collocations(collocations[template], 'chi2_' + template[0] + '_' + template[1] + '.txt')

    def _save_chi2_collocations(self, collocations, file_to_save):
        chi2_collocations = self.tools.get_chi2_collocations_list(collocations)
        file_name = os.path.join(self.dir_to_save, file_to_save)
        with codecs.open(file_name, 'w', 'utf-8') as f:
            f.write("\n".join([
                it[0][0] + " " + it[0][1] + "\t" + str(it[1]) + "\t" + str(self.tools.idf(it[0][0])) + "\t" + str(
                    self.tools.idf(
                        it[0][1])) for it in chi2_collocations]))

    def _save_to(self, file_name, terms):
        with codecs.open(file_name, 'w', 'utf-8') as f:
            term_pairs = sorted(terms.items(), key=lambda x: x[1], reverse=True)
            f.write("\n".join([pair[0][0] + " " + pair[0][1] + "\t" + str(pair[1]) + "\t" + str(self.tools.idf(
                pair[0][0])) + "\t" + str(self.tools.idf(pair[0][1])) for pair in term_pairs]))

    def filter_digits(self, word):
        return not word.isdigit()

    def filter_by_idf(self, word, threshold):
        return self.tools.idf(word) >= threshold

    def filter_fun(self, word):
        return self.filter_digits(word) and self.filter_by_idf(word, 2)

    def coentry_terms(self):
        terms = self.tools.get_coentry_terms(filter_fun=self.filter_fun)
        file_name = os.path.join(self.dir_to_save, self.coentry_terms_file_name)
        self._save_to(file_name, terms)

    def term_dist_cosine_similarity(self):
        dist_matrix = self.tools.dist_matrix()
        terms = self.tools.get_cosine_terms(dist_matrix)
        file_name = os.path.join(self.dir_to_save, self.dist_terms_file_name)
        self._save_to(file_name, terms)

    def term_cosine_similarity(self):
        coentry_terms = self.tools.get_coentry_terms(filter_fun=self.filter_fun)
        coentry_matrix = self.tools.get_coentry_word_matrix(coentry_terms)
        terms = self.tools.get_cosine_terms(coentry_matrix)
        file_name = os.path.join(self.dir_to_save, self.scalar_product_terms_file_name)
        self._save_to(file_name, terms)

    def stable_collocations(self, pos_template_list):
        stable_cols = self.tools.get_stable_collocations(pos_template_list)
        for pos in stable_cols.keys():
            file_name = os.path.join(self.dir_to_save, 'stable_' + pos[0] + '_' + pos[1] + '.txt')
            with codecs.open(file_name, 'w', 'utf-8') as f:
                f.write("\n".join([col[0][0] + " " + col[0][1] + "\t" + str(col[1]) + "\t" + str(self.tools.idf(
                    col[0][0])) + "\t" + str(self.tools.idf(col[0][1])) for col in stable_cols[pos]]))

    def word_idf_distribution(self):
        file_name = os.path.join(self.dir_to_save, self.idf_distrib_file_name)
        terms = set(self.tools.get_terms())
        sorted_terms_idf = sorted([(term, int(round(self.tools.idf(term)))) for term in terms], key=lambda x: x[1])
        with codecs.open(file_name, 'w', 'utf-8') as f:
            f.write("\n".join([it[0] + "\t" + str(it[1]) for it in sorted_terms_idf]))







