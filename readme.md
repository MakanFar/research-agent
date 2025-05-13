<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/MakanFar/research-agent">
    <img src="images/logo.png" alt="Logo" width="120">
  </a>

  <h3 align="center">Research Agent</h3>

  <p align="center">
    A lightweight CLI tool that summarizes research papers using LangChain and OpenAI.
    <br />
    <a href="https://github.com/MakanFar/research-agent"><strong>Explore the Docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/MakanFar/research-agent/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/MakanFar/research-agent/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## 🚀 About The Project

Summarizing scientific papers can be painfully time-consuming. Reading dozens of full-length PDFs, extracting key details, and synthesizing them into a review takes hours of mental effort. That’s why I built **Research Agent** — a command-line tool designed to automate that process.

With Research Agent, you can:

- 🔍 **Find** relevant papers (coming soon)
- 🧹 **Filter** them by quality or custom criteria
- 📖 **Extract structured metadata** 
- 🧾 Output a json or **summary table** of content

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🛠️ Built With

- [LangChain](https://www.langchain.com/)
- [OpenAI GPT-4](https://platform.openai.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [PyPDFLoader](https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf)
- [Python 3.10+](https://www.python.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🧑‍💻 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MakanFar/research-agent.git
   cd research-agent

2. **Install dependencies**
   ```bash
   pip install -e

3. **Set your OpenAI API Key**
Add it to config.yaml:
    ```bash
    openai_api_key: sk-...


(Optional) Adjust config
Configure fields you want extracted:
extract_fields:
  - first_author
  - publication_date
  - title
  - data_type
  - species_breed
  - ml_algorithm
  - ai_goal

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📌 Usage


From the terminal, run:
    ```bash
    python -m research_agent 

This will display a structured summary table of the paper’s keycontent in the terminal, and save the same information as a JSON file if an output path.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🗺 Roadmap

 - [x] Summarization 
 - [x] Configurable metadata extraction
 - [ ] Paper finder and relevance scorer
 - [ ] Q&A with papers

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>