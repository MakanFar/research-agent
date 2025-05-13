from setuptools import setup, find_packages

setup(
    name="research_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain",
        "openai",
        "rich",
        "langchain-community",
        "langchain-openai"
    ],
    entry_points={
        "console_scripts": [
            "research-agent=research_agent.__main__:main",
        ],
    },
)
