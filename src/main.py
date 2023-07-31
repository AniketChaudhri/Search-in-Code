import gradio as gr
from src.embeddings import Embeddings

from src.repo.base import RepoFactory
from sentence_transformers import SentenceTransformer

from src.query import Query

def main(project_link):
    obj = RepoFactory(project_link).make()
    return "Done"
    github = GitHub()
    project = github.clone_repo(project_link)
    # unpack the project
    status, link = project
    if status == False:
        return "Invalid link provided or project size is too large"
    # project=""
    class args:
        path_to_repo= link
        model_name_or_path= 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net'
        batch_size= 32
        query_text= 'perform query'
    query = Query()
    model = SentenceTransformer(args.model_name_or_path)
    return query.perform_query(model, args)
    return link

project_link = gr.Textbox(lines=2, placeholder="Enter github link or local project path", label="Project Link")

gr.Interface(
    fn=main,
    inputs=project_link,
    outputs="text"

).launch()