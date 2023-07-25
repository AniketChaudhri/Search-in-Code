import os
import unittest
from loguru import logger
import gzip
import pickle
import torch
from sentence_transformers import util
from sentence_transformers import SentenceTransformer

from src.embeddings import Embeddings

class Query:
    def __init__(self):
        pass

    def _find_closest_embeddings(self, query_embedding, dataset):
        cosine_similarity = util.cos_sim(query_embedding, dataset['embeddings'])[0]
        top_results = torch.topk(cosine_similarity, k=min(3, len(cosine_similarity)), sorted=True)
        out = []
        for score, idx in zip(top_results[0], top_results[1]):
            out.append((score, dataset['functions'][idx]))
        return out

    def _embeddings_exists(self, args):
        return os.path.isfile(args.path_to_repo + '/' + '.embeddings')

    def create_embeddings(self, model, args):
        embeddings = Embeddings()
        embeddings.embed(args, model)


    def _query_embeddings(self, model, args):
        if not self._embeddings_exists(args):
            # call function to create embeddings
            logger.info("No embeddings found, creating embeddings")
            self.create_embeddings(model, args)
            # pass

        with gzip.open(args.path_to_repo + '/' + '.embeddings', 'r') as f:
            dataset = pickle.loads(f.read())
            # TODO: check if current embeddings model is same as provided
            query_embedding = model.encode(args.query_text, convert_to_tensor=True)
            result = self._find_closest_embeddings(query_embedding, dataset)
            return result

    def perform_query(self, model, args):
        if not args.query_text:
            logger.info("No query text provided")
            return None

        result = self._query_embeddings(model, args)

        return result

if __name__ == "__main__":
    class TestQuery(unittest.TestCase):
        def test_query(self):
            class args:
                path_to_repo= r'C:\Users\S9053161\Documents\projects\Search-in-Code\src\gitrepos\78218'
                model_name_or_path= 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net'
                batch_size= 32
                query_text= 'perform query'

            model = SentenceTransformer(args.model_name_or_path)
            query = Query()
            print(query.perform_query(model, args))


    unittest.main()


