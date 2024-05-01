"""
This main function defines a handler to put a crawler on a Cloud Run function.
The handler function is the entry point for Cloud Run. In Cloud Run, the handler function is invoked when an event triggers it.
"""

from typing import Any
import lib
import argparse
from datetime import datetime
import time

from github import GithubCrawler
from linkedin import LinkedInCrawler
from medium import MediumCrawler
from dispatcher import CrawlerDispatcher
from documents import UserDocument

_dispatcher = CrawlerDispatcher()
#_dispatcher.register("linkedin", LinkedInCrawler)

# use Python’s standard logging library to send logs to GCP
import logging
formatter = logging.basicConfig(format='%(asctime)s %(message)s', level = logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler('log/{:%Y-%m-%d}.log'.format(datetime.now()))
file_handler.setFormatter(formatter)
cl = logging.getLogger()
cl.addHandler(file_handler)

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
                        help='either "medium" or "github" for now.')
    parser.add_argument('--mode', metavar='option', required=True,
                   help='which posts or data to crawl: either "bulk" or "latest".')
    #parser.add_argument('--dem', metavar='path', required=True,
     #                   help='path to dem')
    args = parser.parse_args()
    crawler, mode = args.crawler, args.mode
    
    kevin_linkedin = {
        "user": "Kevin Siswandi",
        "link": "https://www.linkedin.com/in/kevinsiswandi/",
    }
    adrian_linkedin = {
        'user': 'Adrian Nugraha Utama',
        'link' : 'https://www.linkedin.com/in/anuutama'
    }
     
    if crawler == 'github':
        _dispatcher.register("github", GithubCrawler)
        
        if mode == 'latest':
            github_handler = {"user": 'Physicist91', 'link': 'https://github.com/Physicist91/data-tools'}
            handler(github_handler)
        elif mode == 'bulk':
            links = ['https://github.com/Physicist91/uwhpsc',
                     'https://github.com/Physicist91/Physicist91',
                     'https://github.com/Physicist91/ProgrammingAssignment2',
                     'https://github.com/Physicist91/get-clean-data',
                     'https://github.com/Physicist91/RepData_PeerAssessment1',
                     'https://github.com/Physicist91/R_speed_tips',
                     'https://github.com/Physicist91/statistics-dsc5101',
                     'https://github.com/Physicist91/santander2',
                     'https://github.com/Physicist91/talkingdata',
                     'https://github.com/Physicist91/kobe',
                     'https://github.com/Physicist91/sentiment',
                     'https://github.com/Physicist91/contain-yourself',
                     'https://github.com/Physicist91/dvfp',
                     'https://github.com/Physicist91/light-matter',
                     'https://github.com/Physicist91/predmachlearn',
                     'https://github.com/Physicist91/oopfsc',
                     'https://github.com/Physicist91/swiftkey',
                     'https://github.com/Physicist91/sentiment-analysis',
                     'https://github.com/Physicist91/systems-identification',
                     'https://github.com/Physicist91/plagiarism-detector',
                     'https://github.com/Physicist91/sagemaker-template',
                     'https://github.com/Physicist91/covid19',
                     'https://github.com/Physicist91/ml-notes',
                     'https://github.com/Physicist91/clinic-ai',
                     'https://github.com/Physicist91/pytorch-intro',
                     'https://github.com/Physicist91/copd-ml',
                     'https://github.com/Physicist91/genai-quick',
                     'https://github.com/Physicist91/data-tools',
                     'https://github.com/Physicist91/ai-twin',
                     'https://github.com/Physicist91/trading'
            ]
            for link in links:
                handler({"user": 'Physicist91', 'link': link})
                time.sleep(2)
        else:
            raise Exception("Mode {} is not supported.".format(mode))
        
    elif crawler == 'medium':
        _dispatcher.register("medium", MediumCrawler)
        
        if mode == 'latest':
            kevin_medium_latest = {
                "user": "Kevin Siswandi",
                "link" : "https://medium.com/@kevinsiswandi/a-primer-to-language-model-eaf4b41aec5f"
            }
            handler(kevin_medium_latest)
        elif mode == 'bulk': # bulk insert of past posts 
            # downstream also need to handle duplicate posts
            links = ['https://medium.com/@kevinsiswandi/productionalising-machine-learning-models-8ba95fc65457',
                'https://medium.com/@kevinsiswandi/can-we-predict-deadly-chronic-disease-early-using-data-science-d43ac55bea97',
                'https://medium.com/nerd-for-tech/this-interactive-visualization-tool-will-supercharge-your-data-narrative-30a52569acae',
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
                handler({'user':'Kevin Siswandi', 'link':link})
        else:
            raise Exception('Mode is not supported for {}'.format(mode))
        
    else:
        raise Exception("Crawler is not supported for the platform {}".format(crawler))