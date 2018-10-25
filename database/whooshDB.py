from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NGRAM, ID, NUMERIC, STORED, TEXT
import os.path
# from whoosh.index import create_in
# from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh import qparser
from whoosh import analysis

class WhooshDB:
	"whoosh database class"

	def __init__(self, index_dir="whoosh_index", schema_type="", schema_name="default_schema"):
		self.index_dir = index_dir
		self.schema_type = schema_type
		self.schema_name = schema_name
		self.schema_dir = self.index_dir+"/"+self.schema_name
		self.search_limit = 100
		
		analyzer = analysis.StandardAnalyzer(stoplist=frozenset([]))
		# create schema
		if self.schema_type == "dialogs":
			self.schema = Schema(dialog=TEXT(analyzer=analyzer, stored=True), lang=ID(stored=True), turn=NUMERIC(stored=True), vector=STORED)
		elif self.schema_type == "embedding":
			self.schema = Schema(key=ID(stored=True), vector=STORED)
		
		# create index
		if not os.path.exists(self.index_dir):
			os.mkdir(self.index_dir)

		if not os.path.exists(self.schema_dir):
			os.mkdir(self.schema_dir)

		# create / load index
		storage = FileStorage(self.schema_dir)
		# check index exists
		if storage.index_exists():
			print('index exists, loading.')
			# open
			self.ix = storage.open_index()
		else:
			print('index doesn\'t exists, creating.')
			# create
			self.ix = storage.create_index(self.schema)
		
		# open index directory
		# self.ix = open_dir(self.schema_dir)

		self.writer = None

	def writeData(self, data):
		# write documents to the index
		if self.writer == None:
			self.writer = self.ix.writer()
		for data_ in data:
			if self.schema_type == "dialogs":
				self.writer.add_document(dialog=data_["dialog"], lang=data_["lang"], turn=data_["turn"], vector=data_["vector"])
			elif self.schema_type == "embedding":
				self.writer.add_document(key=data_["key"], vector=data_["vector"])

	def commitData(self):
		# writer = self.ix.writer()
		self.writer.commit()
		self.writer = None

	def readData(self, data):
		results = None
		# init searcher
		with self.ix.searcher() as searcher:
			parser = QueryParser(data["query_field"], self.ix.schema, plugins=[], group=qparser.OrGroup)
			# parser.add_plugin(qparser.FuzzyTermPlugin())
			myquery = parser.parse(data["query_str"])
			# print("-=-=-=-=-=-=", parser.filters())
			results = [dict(d_) for d_ in searcher.search(myquery, limit=self.search_limit)]
			# print(parser, myquery)
		return results