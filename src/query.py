from loguru import logger
import gzip
import pickle
import torch
from sentence_transformers import util

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


    def _query_embeddings(self, model, args):
        if not self._embeddings_exists(args):
            # call function to create embeddings
            # create_embeddings(model, args)
            pass

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


