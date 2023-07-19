import tqdm
import os

from tree_sitter import Tree
from tree_sitter_languages import get_parser

from constants import EXTENSIONS
from textwrap import dedent

class Embeddings:
    def __init__(self):
        pass

    def _traverse_tree(tree: Tree):
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

    def _extract_functions(nodes, fp, file_content, relevant_node_types):
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