from setuptools import setup
from setuptools import find_packages

setup(
    name="RedditBotBuilder",
    description="A Python framework for quickly building reddit bots",
    version="1.0.0a1",
    url="https://github.com/Kevinpgalligan/RedditBotBuilder",
    author="Kevin Galligan",
    author_email="galligankevinp@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=["praw", "prawcore"]
)
