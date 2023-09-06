from urllib.request import urlretrieve
from diagrams import Cluster, Diagram, Edge
from diagrams.firebase.develop import RealtimeDatabase, Functions, Authentication
from diagrams.saas.cdn import Cloudflare
from diagrams.aws.network import CF, APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda
from diagrams.aws.security import SecretsManager
from diagrams.aws.ml import Sagemaker, SagemakerModel, SagemakerNotebook, ElasticInference
from diagrams.custom import Custom
from diagrams.onprem.ci import GithubActions
from diagrams.generic.device import Mobile
from diagrams.onprem.vcs import Github

props = dict(fontsize="11", margin="30")

icons = {
    "colab_icon.png": "https://th.bing.com/th/id/OIP.vwkWDhOCtVetzGnJ0p7IAwAAAA?pid=ImgDet&rs=1",
    "eth_icon.png": "https://th.bing.com/th/id/OIP.Lq7thawo-rrIb9gV7fIZOwHaHx?pid=ImgDet&rs=1",
    "mongo_icon.png": "https://asset.brandfetch.io/ideyyfT0Lp/idhHZwYUWa.png",
    "opensea.jpg": "https://asset.brandfetch.io/idxjBvGuV3/idAaTCbE-a.jpeg"
}

for filename, url in icons.items():
    urlretrieve(url, filename)

def get_icon_key(substring):
    return next((key for key in icons.keys() if substring in key), None)

with Diagram("mgxs.co", show=False) as diag:
    with Cluster("CloudFlare", graph_attr=dict(bgcolor="honeydew2", **props)) as cf:
        flare_api = Cloudflare("api.mgxs.co", **props)
        flare_mem = Cloudflare("mem.mgxs.co", **props)
        flare_embed = Cloudflare("embed.mgxs.co", **props)
        flare_tree = Cloudflare("tree.mgxs.co", **props)

    eth = Custom("Ethereum", get_icon_key('eth'), **props)
    mongo = Custom("NFT metadata", get_icon_key('mongo'), **props)

    with Cluster("Google Colab", graph_attr=dict(bgcolor="grey95", **props)):
        colab = Custom("Train / Testing", get_icon_key('colab'), **props)

    with Cluster("Code", direction="BT", graph_attr=dict(bgcolor="grey95", **props)):
        gh_repo = Github("Repositories", **props)
        gh_actions = GithubActions("CI/CD", **props)
        gh_repo >> gh_actions

    with Cluster("Firebase", graph_attr=dict(bgcolor="grey95", **props)):
        fb = Authentication("AppCheck Auth", **props)
        realtime_db = RealtimeDatabase("Database", **props)
        functions_fb = Functions("Functions", **props)
        functions_fb >> [eth, mongo]
        fb >> [realtime_db, functions_fb]

    with Cluster("AWS", graph_attr=dict(**props)):
        aws_secrets = SecretsManager("Secrets", **props)

        with Cluster("CloudFront", graph_attr=dict(bgcolor="grey95", **props)):
            aws_cf_mem = CF("mem.mgxs.co", **props)
            aws_cf_embed = CF("embed.mgxs.co", **props)
            aws_cf_tree = CF("tree.mgxs.co", **props)
            aws_cf_api = CF("api.mgxs.co", **props)

        with Cluster("API Gateway", graph_attr=dict(**props)):
            aws_api = APIGateway("Gateway", **props)
            aws_lambda = Lambda("REST API", **props)

        with Cluster("S3", graph_attr=dict(**props)):
            aws_s3_ai = S3("ai.s3.mgxs.co", **props)
            aws_s3_mem = S3("mem.s3.mgxs.co", **props)
            aws_s3_embed = S3("embed.s3.mgxs.co", **props)
            aws_s3_tree = S3("tree.s3.mgxs.co", **props)
            all_buckets = [aws_s3_mem, aws_s3_embed, aws_s3_tree, aws_s3_ai]

        aws_cf_mem >> aws_s3_mem
        aws_cf_embed >> aws_s3_embed
        aws_cf_tree >> aws_s3_tree

        aws_api >> aws_lambda

        with Cluster("SageMaker", direction="LR", graph_attr=dict(**props)):
            sm = Sagemaker("Endpoint", **props)
            model = SagemakerModel("HuggingFace\nStableDiffusion", **props)
            jupyter = SagemakerNotebook("Create Inference\n& Model upload", **props)
            model_notebook = model - jupyter

            with Cluster(
                "Auto Scaling (up to 10x)",
                direction="LR",
                graph_attr=dict(**props, bgcolor="powderblue"),
            ):
                aws_ml_elastic = ElasticInference("Inference 1\ng5.12xlarge", **props)
                aws_ml_elastic1 = ElasticInference("Inference 2\ng5.12xlarge", **props)
                aws_ml_elastic2 = ElasticInference(
                    "Inference 3...\ng5.12xlarge", **props
                )
                aws_ml_elastic - aws_ml_elastic1 - aws_ml_elastic2

            sm >> aws_ml_elastic >> model

        aws_secrets >> Edge(style="dotted", color="darkred") >> [aws_lambda, gh_actions]

        jupyter >> aws_s3_ai >> model

        aws_lambda >> Edge(color="darkgreen") << [eth, sm, fb, mongo]

        aws_cf_api >> aws_api
        # aws >> fb_db

    # gh_actions >> Edge(style="dotted") >> [*all_buckets, aws_lambda, aws_api, functions_fb]
    # gh_actions >> Edge(style="dotted", label="push") >> [aws_lambda, aws_api, functions_fb]
    # gh_actions >> Edge(style="dotted", label="sync") >> all_buckets

    with Cluster("Internet", graph_attr=dict(bgcolor="grey95", **props)) as internet:
        mobile = Mobile("User", **props)
        opensea = Custom("NFT metadata", get_icon_key('opensea'), **props)

    mobile >> [flare_mem, flare_tree, flare_embed]
    opensea >> flare_api

    flare_mem >> aws_cf_mem
    flare_tree >> aws_cf_tree
    flare_embed >> aws_cf_embed
    flare_api >> aws_cf_api

    jupyter << colab

# diag
