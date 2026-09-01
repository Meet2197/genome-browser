Genome Browser

> A lightweight, full-stack genome browser for exploring plant-associated microbial genomes — annotations, GC content, tRNA/rRNA, mobile genetic elements, SNPs, metagenomic coverage, and comparative genomics — inspired by JBrowse 2 multi-track visualization.

Built with **Flask + SQLite3** (backend/database) and a **vanilla JS/Canvas** frontend, designed to be swapped later for a production-grade **React + JBrowse 2** UI and **SQLite + Object Storage** backend.

---

## ✨ Features

- 🔍 **Search & Filter Genomes** — Filter genomes by name, host plant, or environmental isolation source.
- 🧬 **Multi-Track Genome Viewer** — Render GC content, CDS/genes, tRNA/rRNA, mobile genetic elements, SNPs, and metagenomic coverage depth.
- 🖱️ **Click-to-Inspect Genes** — Inspect product details, EC numbers, functional annotations, KEGG pathways, COG categories, and expression data.
- 🌍 **Environmental Metadata** — View sample location, pH, temperature, and isolation source metadata.
- 🔬 **Real NCBI-Sourced Annotations** — Live annotation data fetched via the NCBI Datasets API v2 for 6 microbial genomes.
- 🧫 **Curated Demo Genome** — *Pseudomonas fluorescens* Pf0-1 with hand-crafted annotation tracks matching reference genome browser mockups.
- 🔗 **Comparative Genomics** — Interactive cross-genome table linking orthologous genes across species.

---

## 🏗️ Architecture

```text
Frontend (HTML/CSS/JS Canvas)
      │
      ▼
Flask REST API
      │
      ▼
SQLite3 Database
  ├── genomes
  ├── genes (CDS)
  ├── rna_features (tRNA/rRNA)
  ├── kegg_pathways
  ├── cog_categories
  ├── mobile_elements
  ├── snps
  ├── gc_windows
  ├── coverage
  ├── expression
  ├── comparative_genomics
  └── environmental_metadata
```

> **Target Architecture:** Designed to scale toward a **React + TypeScript + JBrowse 2** frontend, **Django / FastAPI** microservices backend, **PostgreSQL + PostGIS** database, **Object Storage (S3/MinIO)** for FASTA/BAM/VCF alignment files, and **OpenSearch** for full-text gene indexing.

---

## 📂 Project Structure

```text
Genome_browser/
│
├── main.py                   # Flask app & REST API routes
├── database.py               # SQLite connection helpers & schema init
├── schema.sql                # Full database schema (12 tables)
├── seed_data.py              # Seeds demo + curated real-gene data
├── fetch_ncbi_annotations.py # Pulls live GFF3 annotations from NCBI Datasets API
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
│
└── static/
    ├── index.html            # Main UI layout
    ├── style.css             # Application styling
    └── app.js                # Canvas-based genome track renderer & API integration
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10 – 3.12** recommended *(Python 3.14 works, but avoid packages requiring Rust/C compilation)*
- **pip** package manager

---

### Step-by-Step Installation

#### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/plant-microbiome-genome-browser.git
cd plant-microbiome-genome-browser
```

#### 2. Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Seed the database

```bash
python seed_data.py
```

#### 5. (Optional) Fetch live annotation data from NCBI

```bash
python fetch_ncbi_annotations.py
```

> *Requires internet access. Pulls real GFF3 annotations for all genome accessions stored in the database.*

#### 6. Run the application

```bash
python main.py
```

Open your browser at:
[http://localhost:8000](http://localhost:8000)

---

## 🧬 Included Genomes

| Genome                              | Host Plant               | Environment  | Assembly Accession  |
| :---------------------------------- | :----------------------- | :----------- | :------------------ |
| *Pseudomonas fluorescens* Pf0-1   | *Arabidopsis thaliana* | Rhizosphere  | `GCF_000007765.2` |
| *Bacillus velezensis* FZB42       | *Arabidopsis thaliana* | Rhizosphere  | `GCF_000015785.2` |
| *Streptomyces griseus*            | *Arabidopsis thaliana* | Rhizosphere  | `GCF_000009765.1` |
| *Pseudomonas putida* KT2440       | *Zea mays*             | Rhizosphere  | `GCF_000007565.2` |
| *Burkholderia phytofirmans* PsJN  | *Oryza sativa*         | Endosphere   | `GCF_000020125.1` |
| *Methylobacterium extorquens* PA1 | *Solanum lycopersicum* | Phyllosphere | `GCF_000018345.1` |
| *Streptomyces coelicolor* A3(2)   | —                       | Bulk Soil    | `GCF_000203835.1` |

---

## 🔌 API Endpoints

| Method  | Endpoint                                | Description                                      |
| :------ | :-------------------------------------- | :----------------------------------------------- |
| `GET` | `/api/genomes`                        | List / search / filter genomes                   |
| `GET` | `/api/genomes/<id>`                   | Genome details + environmental metadata          |
| `GET` | `/api/genomes/<id>/genes?start=&end=` | CDS / gene features in a region                  |
| `GET` | `/api/genomes/<id>/rna?start=&end=`   | tRNA / rRNA features in a region                 |
| `GET` | `/api/genomes/<id>/mobile_elements`   | Mobile genetic elements in a region              |
| `GET` | `/api/genomes/<id>/snps`              | SNP / variant positions in a region              |
| `GET` | `/api/genomes/<id>/gc`                | GC content windows                               |
| `GET` | `/api/genomes/<id>/coverage`          | Metagenomic read coverage depth                  |
| `GET` | `/api/genomes/<id>/first_genes`       | First annotated genes (used for auto-navigation) |
| `GET` | `/api/genes/<id>`                     | Full gene detail: product, KEGG, COG, expression |
| `GET` | `/api/search?q=`                      | Full-text search across gene names / products    |
| `GET` | `/api/genomes/<id>/comparative`       | Comparative genomics / ortholog links            |

---

## 📜 License

Distributed under the **MIT License** — free to use, modify, and distribute.

