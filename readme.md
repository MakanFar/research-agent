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
    An agent that retrieves, screens, and summarizes research papers using OpenAI and LangChain.
    <br />
    <a href="https://github.com/MakanFar/research-agent"><strong>Explore the Docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/MakanFar/research-agent/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/MakanFar/research-agent/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
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

Summarizing scientific literature is time-consuming. Research Agent automates this process:

- 🔍 Retrieves papers from PubMed Central
- 📄 Screens abstracts using your review objective
- 📊 Performs structured meta-analysis or systematic review
- 💾 Outputs clean JSON with summaries and metadata

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🛠️ Built With

- [LangChain](https://www.langchain.com/)
- [OpenAI GPT-4o](https://platform.openai.com/)
- [Typer CLI](https://typer.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)
- [Python 3.10+](https://www.python.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🧑‍💻 Getting Started

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key [Get the key!](https://openai.com/api/)
- A NCBI API key [Get the key!](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)

### Installation

```bash
git clone https://github.com/MakanFar/research-agent.git
cd research-agent
pip install .
```

### Configuration

Edit or create `config.yaml` in the root directory:

#### 🔑 API Keys
- you can add your API keys to the config:
  
```yaml
OPENAI_API_KEY: sk-...
NCBI_API_KEY: ...
```

Alternatively, you can export them as environment variables:

```bash
export OPENAI_API_KEY=sk-...
export NCBI_API_KEY=...
```

#### 🔍 Default Search Query
Specify a PubMed Central query:

```yaml
search_query: ("Artificial intelligence"[Title/Abstract] AND "Protein-protein interaction")
```
You can also provide the query directly via the CLI at runtime.


#### 🧾 Metadata Extraction (from abstracts)
Customize fields to extract during meta-analysis or systematic review:

```yaml
meta_data:
     - data_type: Type of data used in the study such as radiology, clinicopathologic, or text
    - species_breed: Target species
    - ml_algorithm: Types Model used in the study
    - ai_goal: Clinical objective of the study
    - performance_results: Key final performance results
```
Note: The agent always extracts the following by default:

- Year
- First Author
- Title
- Journal
- PMCID
- URL


#### 📘 Full-Text Extraction (systematic review only)
Optional deep extraction from full papers:

```yaml
in_depth:
  - small_dataset: Short explanation if fewer than ~1000 samples OR authors mention limited data.
```



<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📌 Usage

### Run the CLI
```bash
research_agent analyze
```

You will be prompted to:
- Select a review type: `meta` or `systematic`
- Enter a search query (or load from config.yaml)
- Provide a screening objective (if filtering is enabled)

### Example
```bash
research_agent analyze \
  --task meta \
  --objective "AI for diagnosing UTIs in dogs" \
  --filter-papers True \
  --max-results 100 \
  --output-dir ./output
```

### Outputs

- `paper_screenings.json`: Results of the screening step
```json
{
    "relevant": false,
    "reason": "The study does not involve the application of AI techniques such as machine learning or deep learning",
    "confidence": "High",
    "pmc": "PMC9554590",
    "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9554590/",
    "title": "Contrast-enhanced ultrasound features of focal pancreatic lesions in cats",
    "Author": "Silvia Burti",
    "year": "2022",
    "journal": "Frontiers in Veterinary Science"
  }
```

- `paper_summaries.json`: Meta-analysis or systematic review output

```json
  {
    "meta_data": {
      "pmc": "PMC11271534",
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11271534/",
      "title": "Exploring deep learning strategies for intervertebral disc herniation detection on veterinary MRI",
      "journal": "Scientific Reports",
      "first_author": "Shoujin Huang",
      "year": "2024"
    },
    "body_data": {
      "small_dataset": "The study used 487 MRI images from 213 dogs, which is relatively small for deep learning applications.",
    }
  }
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🗺 Roadmap

- [x] Paper screening and summarization
- [x] Configurable metadata fields
- [ ] Support local PDFs
- [ ] Interactive Q&A over papers
- [ ] Semantic Scholar and ArXiv support

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🧾 License

Distributed under the MIT License. See `LICENSE` for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
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
