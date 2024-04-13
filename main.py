"""
This main function defines a handler to put a crawler on a Cloud Run function.
The handler function is the entry point for Cloud Run. In Cloud Run, the handler function is invoked when an event triggers it.
"""

from typing import Any
import lib
import argparse

from github import GithubCrawler
from linkedin import LinkedInCrawler
from medium import MediumCrawler
from dispatcher import CrawlerDispatcher
from documents import UserDocument

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


def handler(event) -> dict[str, Any]:
    first_name, last_name = lib.user_to_names(event.get("user"))
    
    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Link processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    """
    # Development only: run "python main.py" and test locally
    """
    parser = argparse.ArgumentParser(description='Create the ETL schema')
    parser.add_argument('--crawler', metavar='platform', required=True,
                        help='either "medium" or "github"')
    #parser.add_argument('--schema', metavar='path', required=True,
     #                   help='path to schema')
    #parser.add_argument('--dem', metavar='path', required=True,
     #                   help='path to dem')
    args = parser.parse_args()
    model_schema(workspace=args.workspace, schema=args.schema, dem=args.dem)
    
    kevin_linkedin = {
        "user": "Kevin Siswandi",
        "link": "https://www.linkedin.com/in/kevinsiswandi/",
    }
    adrian_linkedin = {
        'user': 'Adrian Nugraha Utama',
        'link' : 'https://www.linkedin.com/in/anuutama'
    }
    kevin_medium_latest = {
        "user": "Kevin Siswandi",
        "link" : "https://medium.com/@kevinsiswandi/can-we-predict-deadly-chronic-disease-early-using-data-science-d43ac55bea97"
    }
    
    # if medium (bulk insert of past posts) is selected
    # downstream also need to handle duplicate posts
    links = ['https://medium.com/nerd-for-tech/this-interactive-visualization-tool-will-supercharge-your-data-narrative-30a52569acae',
            'https://medium.com/@kevinsiswandi/family-tree-of-indonesias-famous-individuals-e2c9ade360a3',
            'https://medium.com/@kevinsiswandi/the-data-science-process-135c76c0926b',
            'https://medium.com/@kevinsiswandi/a-slice-of-social-psychology-expectations-matter-3b840fc8cf84',
            'https://medium.com/@kevinsiswandi/agile-methods-kanban-vs-scrum-4d797ee1944',
            'https://medium.com/@kevinsiswandi/introduction-to-agile-methodology-bd3c7617cdfa',
            'https://medium.com/@kevinsiswandi/7-steps-to-acing-a-coding-interview-325e034723ab',
            'https://medium.com/@kevinsiswandi/introduction-to-cell-and-molecular-biology-for-non-biologists-527bb4a95d3f',
            'https://medium.com/@kevinsiswandi/menu-of-topics-for-a-machine-learning-interview-d7c7c2f81f43',
            'https://medium.com/@kevinsiswandi/5-tips-for-preparing-for-data-science-interview-78dd38b056e0',
            'https://medium.com/@kevinsiswandi/on-data-science-data-analysis-and-machine-learning-f00cf6aa98f3',
            'https://medium.com/@kevinsiswandi/introduction-to-artificial-intelligence-for-medicine-b0fad1aedd5a',
            'https://medium.com/@kevinsiswandi/tutorial-of-the-star-method-for-answering-behavioural-interview-questions-415a038551cc']
    for link in links:
        medium_handler = {'user':'Kevin Siswandi', 'link':link}
        handler(medium_handler)