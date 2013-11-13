import Aot
from Profiler import Profiler
from TextToolsOutput import TextToolsOutput
from Dict.PosTemplates import pos_templates

dir_to_save = "Data/out"
p = Profiler()
p.start("Start...")

titles = Aot.read_text("Data/GofraTest/OrderNames.txt")
p.done("Reading text")

toolsOutput = TextToolsOutput(titles, dir_to_save)
p.done("TextTools initialization")

toolsOutput.chi2_collocations()
p.done("Chi-square collocations")

toolsOutput.chi2_collocations(pos_templates)
p.done("Chi-square pos_tagged collocations")

toolsOutput.frequent_collocations(pos_templates)
p.done("Frequent collocations")

toolsOutput.coentry_terms()
p.done("Cooccurrent terms search")

toolsOutput.stable_collocations(pos_templates)
p.done("Stable collocations")

toolsOutput.word_idf_distribution()
p.done("Term idf distribution")

toolsOutput.term_dist_cosine_similarity()
p.done("Mean distances vectors cosine similarity")

toolsOutput.term_cosine_similarity()
p.done("Term scalar products")
p.stop()