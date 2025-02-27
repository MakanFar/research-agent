from setuptools import setup, find_packages

setup(
    name="paper_summarizer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain",
        "openai",
        "rich",
        "pyyaml",
        "pypdf"
    ],
    entry_points={
        "console_scripts": [
            "paper-summarizer=paper_summarizer.__main__:main",
        ],
    },
)
