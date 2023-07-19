import gzip
import pickle
import unittest
import numpy as np
from tqdm import tqdm
import os
import sys

from tree_sitter import Tree
from tree_sitter_languages import get_parser

from constants import EXTENSIONS
from textwrap import dedent
from sentence_transformers import SentenceTransformer

class Embeddings:
    def __init__(self):
        pass

    def _traverse_tree(self, tree: Tree):
        cursor = tree.walk()
        reached_root = False
        while reached_root is False:
            yield cursor.node
            if cursor.goto_first_child():
                continue
            if cursor.goto_next_sibling():
                continue
            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True
                if cursor.goto_next_sibling():
                    retracing = False

    def _extract_functions(self, nodes, fp, file_content, relevant_node_types):
        out = []
        for n in nodes:
            if n.type in relevant_node_types:
                node_text = dedent('\n'.join(file_content.split('\n')[
                                    n.start_point[0]:n.end_point[0]+1]))
                out.append(
                    {'file': fp, 'line': n.start_point[0], 'text': node_text})
        return out

    def _get_functions(self, repo_path, extract_nodes):
        functions = []
        print('Extracting functions from {}'.format(repo_path))
        for fp in tqdm([repo_path + '/' + f for f in os.popen('git -C {} ls-files'.format(repo_path)).read().split('\n')]):
            if not os.path.isfile(fp):
                continue
            with open(fp, 'r') as f:
                lang = EXTENSIONS.get(fp[fp.rfind('.'):])
                if lang:
                    parser = get_parser(lang)
                    try:
                        file_content = f.read()
                    except UnicodeDecodeError:
                        file_content = ''
                    tree = parser.parse(bytes(file_content, 'utf8'))
                    all_nodes = list(self._traverse_tree(tree.root_node))
                    functions.extend(self._extract_functions(
                        all_nodes, fp, file_content, extract_nodes))
        return functions

    def embed(self, args, model):
        nodes_to_extract = ['function_definition', 'method_definition',
                        'function_declaration', 'method_declaration']
        functions = self._get_functions(
            args.path_to_repo, nodes_to_extract)

        if not functions:
            print('No supported languages found in {}. Exiting'.format(args.path_to_repo))
            sys.exit(1)

        print('Embedding {} functions in {} batches. This is done once and cached in .embeddings'.format(
            len(functions), int(np.ceil(len(functions)/args.batch_size))))
        corpus_embeddings = model.encode(
            [f['text'] for f in functions], convert_to_tensor=True, show_progress_bar=True, batch_size=args.batch_size)

        dataset = {'functions': functions,
                'embeddings': corpus_embeddings, 'model_name': args.model_name_or_path}

        # dump dataset
        with open(args.path_to_repo + '/' + '.embeddings.log', 'w') as f:
            f.write('dataset: {}\n'.format(dataset))

        with gzip.open(args.path_to_repo + '/' + '.embeddings', 'w') as f:
            f.write(pickle.dumps(dataset))
        return dataset

if __name__ == "__main__":
    class TestEmbeddings(unittest.TestCase):

        def testembed(self):
            class args:
                path_to_repo= r'C:\Users\S9053161\Documents\projects\Search-in-Code\src\gitrepos\78218'
                model_name_or_path= 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net'
                batch_size= 32

            # args={
            #     'path_to_repo': r'C:\Users\S9053161\Documents\projects\Search-in-Code\src\gitrepos\78218',
            #     'model_name_or_path': 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net',
            #     'batch_size': 32
            # }
            model = SentenceTransformer(args.model_name_or_path)
            embeddings = Embeddings()
            print(embeddings.embed(args, model))

    RUN_ALL = False
    if RUN_ALL:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        suite.addTest(TestEmbeddings('testembed'))
        runner = unittest.TextTestRunner()
        runner.run(suite)