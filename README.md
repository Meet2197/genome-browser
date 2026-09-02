# 🧬 Plant Microbiome Genome Browser

> A lightweight, full-stack genome browser for exploring plant-associated microbial genomes through interactive multi-track visualization, functional annotation, comparative genomics, environmental metadata, and sequence-based genomic features.

The project is inspired by modern genome browsers such as JBrowse and provides a practical foundation for building scalable genomic data exploration platforms.

Built with **Python, Flask, SQLite, JavaScript, HTML5 Canvas, and REST APIs**, the application provides an interactive environment for exploring microbial genomes associated with plants, soil, and agricultural ecosystems.

---

## 🚀 Overview

Modern genomic datasets contain multiple layers of biological information, including:

* Genome sequences
* Coding sequences and genes
* Functional annotations
* tRNA and rRNA features
* GC content
* SNPs and variants
* Mobile genetic elements
* Metagenomic coverage
* Environmental metadata
* Comparative genomics relationships

This project integrates these datasets into a single browser-based application.

The architecture is intentionally lightweight for research, prototyping, and educational purposes while providing a clear migration path toward production-grade technologies such as **React, TypeScript, JBrowse 2, FastAPI, object storage, and OpenSearch**.

---

# ✨ Features

## 🔍 Genome Search and Discovery

Search and filter microbial genomes using multiple biological and environmental attributes.

Supported filters include:

* Genome name
* Organism
* Host plant
* Environmental source
* Isolation source

This enables researchers to quickly identify genomes relevant to specific plant microbiome or agricultural research questions.

---

## 🧬 Interactive Multi-Track Genome Viewer

The genome viewer supports multiple biological data tracks.

### Available tracks

| Track                   | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| 🧬 Genes / CDS          | Protein-coding genes and coding sequences             |
| 🧪 GC Content           | Genomic GC composition across genomic windows         |
| 🧫 tRNA / rRNA          | RNA features and genomic positions                    |
| 🦠 Mobile Elements      | Mobile genetic elements                               |
| 🔬 SNPs                 | Single nucleotide polymorphisms and variant positions |
| 📊 Coverage             | Metagenomic sequencing coverage depth                 |
| 🧬 Comparative Genomics | Ortholog relationships across genomes                 |

The frontend uses **JavaScript and HTML5 Canvas** to render genomic regions dynamically.

---

## 🖱️ Gene Inspection

Users can select genomic features to inspect detailed biological information.

Gene-level information may include:

* Gene name
* Product description
* Functional annotation
* EC numbers
* KEGG pathways
* COG categories
* Protein accession
* Expression information

This provides a direct connection between genome visualization and biological interpretation.

---

## 🌍 Environmental Metadata

The platform integrates genomic data with environmental and sample metadata.

Supported metadata may include:

* Geographic location
* Host plant
* Isolation source
* Environmental conditions
* pH
* Temperature
* Sample type

This is particularly important for plant microbiome research because genomic characteristics can be interpreted alongside environmental context.

---

## 🔬 NCBI Annotation Integration

The project includes scripts for retrieving genome annotations from the NCBI ecosystem.

The annotation workflow can retrieve genomic annotation data and populate the local application database.

```text
NCBI Genome Data
        │
        ▼
Annotation Retrieval
        │
        ▼
GFF3 / Genome Features
        │
        ▼
  SQLite Database
        │
        ▼
    REST API
        │
        ▼
Interactive Genome Browser
```

---

## 🧫 Curated Demo Genome

The application includes curated genome data for demonstration and testing purposes.

A primary demonstration genome is:

**Pseudomonas fluorescens Pf0-1**

The dataset includes curated genomic tracks designed to demonstrate the capabilities of a multi-track genome browser.

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│                 Frontend                    │
│                                             │
│       HTML + CSS + JavaScript + Canvas      │
└──────────────────────┬──────────────────────┘
                       │
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│               Flask Backend                 │
│                                             │
│        API Routes + Business Logic          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────┐
│               SQLite Database              │
│                                            │
│  • Genomes                                 │
│  • Genes / CDS                             │
│  • RNA Features                            │
│  • KEGG Pathways                           │
│  • COG Categories                          │
│  • Mobile Elements                         │
│  • SNPs                                    │
│  • GC Windows                              │
│  • Coverage                                │
│  • Expression                              │
│  • Comparative Genomics                    │
│  • Environmental Metadata                  │
└────────────────────────────────────────────┘
```

The repository currently follows a lightweight architecture suitable for local development and research prototyping.

---

# 📂 Project Structure

```text
genome-browser/
│
├── main.py
│   └── Flask application and REST API routes
│
├── database.py
│   └── SQLite connection and database utilities
│
├── schema.sql
│   └── Database schema
│
├── seed_data.py
│   └── Demo and curated biological data
│
├── seed_wheat_microbiome.py
│   └── Wheat microbiome dataset seeding
│
├── fetch_ncbi_annotations.py
│   └── Retrieve genome annotations
│
├── download_genome_fasta.py
│   └── Download genome FASTA sequences
│
├── find_orthologs_by_product.py
│   └── Ortholog discovery utilities
│
├── storage_client.py
│   └── Storage abstraction utilities
│
├── requirements.txt
│   └── Python dependencies
│
├── workflows_python/
│   └── Data processing workflows
│
├── scripts/
│   └── Supporting scripts
│
├── storage/
│   └── Genome and sequence storage
│
└── static/
    │
    ├── index.html
    │   └── Application interface
    │
    ├── style.css
    │   └── Application styling
    │
    └── app.js
        └── Genome visualization and API integration
```

---

# 🛠️ Technology Stack

## Backend

* Python
* Flask
* REST API architecture

## Database

* SQLite

## Frontend

* HTML5
* CSS3
* JavaScript
* HTML5 Canvas

## Genomics and Data Processing

* FASTA
* GFF3
* Genome annotations
* Comparative genomics
* Functional annotations

## External Data Integration

* NCBI genomic data services

---

# 📋 Prerequisites

Before installation, ensure that you have:

* Python 3.10 or newer
* pip
* Git

Recommended Python version:

```text
Python 3.10 – 3.12
```

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Meet2197/genome-browser.git
cd genome-browser
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Initialize and Seed the Database

```bash
python seed_data.py
```

Depending on the dataset you want to load, additional seeding scripts may also be available.

For example:

```bash
python seed_wheat_microbiome.py
```

---

## 5. Fetch Genome Annotations

Optional:

```bash
python fetch_ncbi_annotations.py
```

This step retrieves and processes genomic annotations for genomes configured in the application.

---

## 6. Run the Application

```bash
python main.py
```

The application should then be available locally at:

```text
http://localhost:8000
```

---

# 🔌 REST API

## Genomes

### List or Search Genomes

```http
GET /api/genomes
```

Example:

```text
/api/genomes?q=Pseudomonas
```

---

### Genome Details

```http
GET /api/genomes/<id>
```

Returns genome information together with associated environmental metadata.

---

# 🧬 Genomic Feature APIs

## Genes

```http
GET /api/genomes/<id>/genes?start=<start>&end=<end>
```

Returns coding sequences and genes located within a genomic region.

---

## RNA Features

```http
GET /api/genomes/<id>/rna?start=<start>&end=<end>
```

Returns:

* tRNA
* rRNA
* Other RNA features

---

## Mobile Genetic Elements

```http
GET /api/genomes/<id>/mobile_elements
```

---

## SNPs and Variants

```http
GET /api/genomes/<id>/snps
```

---

## GC Content

```http
GET /api/genomes/<id>/gc
```

---

## Sequencing Coverage

```http
GET /api/genomes/<id>/coverage
```

---

# 🔎 Gene Search

```http
GET /api/search?q=<query>
```

Example:

```text
/api/search?q=transporter
```

The search can be used to identify genes and products across the genomic datasets.

---

# 🔬 Gene Details

```http
GET /api/genes/<id>
```

Potential information includes:

```text
Gene
├── Name
├── Product
├── Functional Annotation
├── EC Number
├── KEGG Pathway
├── COG Category
├── Protein Accession
└── Expression Data
```

---

# 🧬 Comparative Genomics

The application provides comparative genomic relationships between orthologous genes.

```http
GET /api/genomes/<id>/comparative
```

This endpoint can be used to support workflows such as:

* Cross-species gene comparison
* Functional conservation analysis
* Ortholog discovery
* Plant-associated microbiome research

---

# 🧫 Included Genomes

The project includes plant-associated and environmental microbial genomes, including organisms associated with:

* Rhizosphere environments
* Endosphere environments
* Phyllosphere environments
* Soil ecosystems

Examples include:

| Genome                              | Host / Environment |
| ----------------------------------- | ------------------ |
| *Pseudomonas fluorescens* Pf0-1   | Rhizosphere        |
| *Bacillus velezensis* FZB42       | Rhizosphere        |
| *Streptomyces griseus*            | Rhizosphere        |
| *Pseudomonas putida* KT2440       | Rhizosphere        |
| *Burkholderia phytofirmans* PsJN  | Endosphere         |
| *Methylobacterium extorquens* PA1 | Phyllosphere       |
| *Streptomyces coelicolor* A3(2)   | Soil               |

---

# 🔄 Data Workflow

```text
External Genome Sources
        │
        ▼
FASTA / Annotation Data
        │
        ▼
Data Processing Scripts
        │
        ▼
SQLite Database
        │
        ├── Genome Metadata
        ├── Genes
        ├── RNA Features
        ├── SNPs
        ├── GC Windows
        ├── Coverage
        └── Comparative Data
        │
        ▼
Flask REST API
        │
        ▼
Genome Browser Frontend
        │
        ▼
Interactive Research Exploration
```

---

# 🧪 Development

For development, activate the virtual environment:

```bash
venv\Scripts\activate
```

Then run:

```bash
python main.py
```

For database inspection, you can use the SQLite command-line interface:

```bash
sqlite3 genome.db
```

Check available tables:

```sql
.tables
```

Inspect genomes:

```sql
SELECT * FROM genomes;
```

Exit:

```sql
.quit
```

---

# 🗺️ Production Roadmap

The current implementation provides a research and prototype foundation.

Future development can include:

## Frontend

* React
* TypeScript
* JBrowse 2 integration
* WebGL rendering
* Advanced genomic navigation
* Interactive track configuration

## Backend

* FastAPI
* Django REST Framework
* Microservices
* Background processing
* Job queues

## Storage

* S3-compatible object storage
* MinIO
* FASTA storage
* BAM alignment storage
* VCF variant storage

## Search

* OpenSearch
* Elasticsearch
* Full-text gene indexing
* Semantic biological search

## Advanced Analytics

* Genome comparison pipelines
* Functional enrichment
* Machine learning
* Metagenomic analysis
* Pan-genome analysis
* AI-assisted annotation

---

# 🧑‍🔬 Research Use Cases

This platform can support:

* Plant microbiome research
* Agricultural genomics
* Microbial genome exploration
* Comparative genomics
* Functional gene analysis
* Environmental genomics
* Metagenomics
* Genome annotation exploration
* Bioinformatics education

---

# 🤝 Contributing

Contributions are welcome.

Recommended workflow:

```bash
# Fork the repository

# Create a feature branch
git checkout -b feature/my-feature

# Make changes

# Commit changes
git commit -m "Add my feature"

# Push branch
git push origin feature/my-feature
```

Then create a Pull Request.

---

# 📄 License

This project is distributed under the **MIT License**.

You are free to:

* Use
* Modify
* Distribute
* Build upon

the software under the terms of the MIT License.
