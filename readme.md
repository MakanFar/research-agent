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
   pip install .

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
    research_agent 

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

Distributed under the Unlicense License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/makan-farhoodi-470120133/
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 