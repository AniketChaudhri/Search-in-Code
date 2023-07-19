import gradio as gr

from src.github import GitHub

def main(project_link):
    github = GitHub()
    project = github.clone_repo(project_link)
    # unpack the project
    status, link = project
    if status == False:
        return "Invalid link provided or project size is too large"
    # project=""
    return link

project_link = gr.Textbox(lines=2, placeholder="Enter github link or local project path")

gr.Interface(
    fn=main,
    inputs="text",
    outputs="text"

).launch()