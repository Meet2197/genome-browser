

Conversation with Gemini

create readme.md file for this text :







\# 🌱 Plant Microbiome Genome BrowserA lightweight, full-stack genome browser for exploring plant-associated microbial genomes — annotations, GC content, tRNA/rRNA, mobile genetic elements, SNPs, metagenomic coverage, and comparative genomics — inspired by JBrowse2-style multi-track visualization.Built with \*\*Flask + SQLite3\*\* (backend/database) and a \*\*vanilla JS/Canvas\*\* frontend, designed to be swapped later for a production-grade \*\*React + JBrowse2\*\* UI and \*\*PostgreSQL + Object Storage\*\* backend.---## ✨ Features- 🔍 \*\*Search \& filter genomes\*\* by name, host plant, or environment- 🧬 \*\*Multi-track genome viewer\*\*: GC content, CDS/genes, tRNA/rRNA, mobile elements, SNPs, metagenomic coverage- 🖱️ \*\*Click-to-inspect genes\*\*: view product, EC number, function, KEGG pathway, COG category, and expression data- 🌍 \*\*Environmental metadata\*\*: sample location, pH, temperature, isolation source- 🔬 \*\*Real NCBI-sourced annotations\*\* for 6 plant-associated microbial genomes (fetched live via NCBI Datasets API v2)- 🧫 \*\*Curated demo genome\*\* (\*Pseudomonas fluorescens\* Pf0-1) with hand-crafted annotation tracks matching a reference genome browser mockup- 🔗 \*\*Comparative genomics\*\* table linking orthologous genes across genomes---## 🏗️ Architecture







Frontend (HTML/CSS/JS Canvas) │ ▼ Flask REST API │ ▼ SQLite3 Database ├── genomes ├── genes (CDS) ├── rna\_features (tRNA/rRNA) ├── kegg\_pathways ├── cog\_categories ├── mobile\_elements ├── snps ├── gc\_windows ├── coverage ├── expression ├── comparative\_genomics └── environmental\_metadata







> Designed to scale toward: \*\*React + TypeScript + JBrowse2\*\* frontend, \*\*Django/FastAPI\*\* backend, \*\*PostgreSQL + PostGIS\*\*, \*\*Object Storage (S3/MinIO)\*\* for FASTA/BAM/VCF, and \*\*OpenSearch\*\* for full-text search — matching a full production genome-browser architecture for metagenomics research platforms.---## 📂 Project Structure







Genome\_browser/ │ ├── main.py # Flask app \& REST API routes ├── database.py # SQLite connection helpers \& schema init ├── schema.sql # Full database schema (12 tables) ├── seed\_data.py # Seeds demo + curated real-gene data ├── fetch\_ncbi\_annotations.py # Pulls live GFF3 annotations from NCBI Datasets API ├── requirements.txt ├── .gitignore ├── README.md │ └── static/ ├── index.html # Main UI layout ├── style.css # Styling └── app.js # Canvas-based genome track renderer + API calls







\---## 🚀 Getting Started### Prerequisites- Python 3.10 – 3.12 recommended (3.14 works but avoid packages requiring Rust/C compilation)- pip### 1. Clone the repository```bashgit clone https://github.com/<your-username>/plant-microbiome-genome-browser.gitcd plant-microbiome-genome-browser







2\. Create a virtual environment



python -m venv venv# Windows.\\venv\\Scripts\\Activate.ps1# macOS/Linuxsource venv/bin/activate







3\. Install dependencies



pip install -r requirements.txt







4\. Seed the database



python seed\_data.py







5\. (Optional) Fetch real annotation data from NCBI



python fetch\_ncbi\_annotations.py







Requires internet access. Pulls real GFF3 annotations for all genome accessions stored in the database.



6\. Run the app



python main.py







Open your browser at:







http://localhost:8000







🧬 Included Genomes



GenomeHost PlantEnvironmentAssembly AccessionPseudomonas fluorescens Pf0-1Arabidopsis thalianaRhizosphereGCF\_000007765.2Bacillus velezensis FZB42Arabidopsis thalianaRhizosphereGCF\_000015785.2Streptomyces griseusArabidopsis thalianaRhizosphereGCF\_000009765.1Pseudomonas putida KT2440Zea maysRhizosphereGCF\_000007565.2Burkholderia phytofirmans PsJNOryza sativaEndosphereGCF\_000020125.1Methylobacterium extorquens PA1Solanum lycopersicumPhyllosphereGCF\_000018345.1Streptomyces coelicolor A3(2)—Bulk SoilGCF\_000203835.1



🔌 API Endpoints



EndpointDescriptionGET /api/genomesList/search/filter genomesGET /api/genomes/<id>Genome details + environmental metadataGET /api/genomes/<id>/genes?start=\&end=CDS/gene features in a regionGET /api/genomes/<id>/rna?start=\&end=tRNA/rRNA features in a regionGET /api/genomes/<id>/mobile\_elementsMobile genetic elements in a regionGET /api/genomes/<id>/snpsSNP/variant positions in a regionGET /api/genomes/<id>/gcGC content windowsGET /api/genomes/<id>/coverageMetagenomic read coverage depthGET /api/genomes/<id>/first\_genesFirst annotated genes (used for auto-navigation)GET /api/genes/<id>Full gene detail: product, KEGG, COG, expressionGET /api/search?q=Full-text search across gene names/productsGET /api/genomes/<id>/comparativeComparative genomics / ortholog links



🛣️ Roadmap



&#x20;Replace Canvas renderer with real JBrowse 2 React component



&#x20;Migrate SQLite → PostgreSQL + PostGIS



&#x20;Add Object Storage (S3/MinIO) for FASTA/BAM/VCF files



&#x20;Integrate OpenSearch for full-text gene/genome search



&#x20;Add KEGG/COG annotation pipeline (eggNOG-mapper) for real-data genomes



&#x20;Add Nextflow pipelines for annotation, comparative genomics, and metagenomics



&#x20;User authentication \& saved bookmarks/sessions



&#x20;Genome comparison / synteny view



📜 License



MIT License — free to use, modify, and distribute.







🙏 Acknowledgments



Genome annotation data sourced from NCBI Datasets API v2



Inspired by JBrowse 2 genome visualization architecture 



Target Architecture: Designed to scale toward a React + TypeScript + JBrowse 2 frontend, Django / FastAPI microservices backend, PostgreSQL + PostGIS database, Object Storage (S3/MinIO) for FASTA/BAM/VCF alignment files, and OpenSearch for full-text gene indexing — matching production-grade metagenomics research platforms.



📂 Project Structure

Plaintext

Genome\_browser/

│

├── main.py                   # Flask app \& REST API routes

├── database.py               # SQLite connection helpers \& schema init

├── schema.sql                # Full database schema (12 tables)

├── seed\_data.py              # Seeds demo + curated real-gene data

├── fetch\_ncbi\_annotations.py # Pulls live GFF3 annotations from NCBI Datasets API

├── requirements.txt          # Python dependencies

├── .gitignore                # Git ignore rules

├── README.md                 # Project documentation

│

└── static/

&#x20;   ├── index.html            # Main UI layout

&#x20;   ├── style.css             # Application styling

&#x20;   └── app.js                # Canvas-based genome track renderer \& API integration

🚀 Getting Started

Prerequisites

Python 3.10 – 3.12 recommended (Python 3.14 works, but avoid packages requiring Rust/C compilation)



pip package manager



Step-by-Step Installation

1\. Clone the repository

Bash

git clone \[https://github.com/](https://github.com/)<your-username>/plant-microbiome-genome-browser.git

cd plant-microbiome-genome-browser

2\. Create and activate a virtual environment

Bash

\# Create virtual environment

python -m venv venv



\# Windows (PowerShell)

.\\\\venv\\\\Scripts\\\\Activate.ps1



\# macOS / Linux

source venv/bin/activate

3\. Install dependencies

Bash

pip install -r requirements.txt

4\. Seed the database

Bash

python seed\_data.py

5\. (Optional) Fetch live annotation data from NCBI

Bash

python fetch\_ncbi\_annotations.py

Note: Requires internet access. Pulls live GFF3 annotation data for all genome accessions stored in the database.



6\. Launch the application

Bash

python main.py

Open your browser and navigate to:

http://localhost:8000



🧬 Included Genomes

Genome	Host Plant	Environment	Assembly Accession

Pseudomonas fluorescens Pf0-1	Arabidopsis thaliana	Rhizosphere	GCF\_000007765.2

Bacillus velezensis FZB42	Arabidopsis thaliana	Rhizosphere	GCF\_000015785.2

Streptomyces griseus	Arabidopsis thaliana	Rhizosphere	GCF\_000009765.1

Pseudomonas putida KT2440	Zea mays	Rhizosphere	GCF\_000007565.2

Burkholderia phytofirmans PsJN	Oryza sativa	Endosphere	GCF\_000020125.1

Methylobacterium extorquens PA1	Solanum lycopersicum	Phyllosphere	GCF\_000018345.1

Streptomyces coelicolor A3(2)	—	Bulk Soil	GCF\_000203835.1

🔌 API Endpoints

Method	Endpoint	Description

GET	/api/genomes	List, search, or filter genomes

GET	/api/genomes/<id>	Fetch genome details + environmental metadata

GET	/api/genomes/<id>/genes?start=\&end=	Retrieve CDS/gene features in a specified genomic region

GET	/api/genomes/<id>/rna?start=\&end=	Retrieve tRNA/rRNA features in a region

GET	/api/genomes/<id>/mobile\_elements	Get mobile genetic elements in a region

GET	/api/genomes/<id>/snps	Query SNP / variant positions in a region

GET	/api/genomes/<id>/gc	Fetch GC content windows

GET	/api/genomes/<id>/coverage	Retrieve metagenomic read coverage depth

GET	/api/genomes/<id>/first\_genes	Get first annotated genes (used for auto-navigation)

GET	/api/genes/<id>	Full gene detail: product, KEGG, COG, expression

GET	/api/search?q=	Full-text search across gene names and products

GET	/api/genomes/<id>/comparative	Comparative genomics \& ortholog links

🛣️ Roadmap

\[ ] Replace Canvas renderer with real JBrowse 2 React component



\[ ] Migrate SQLite → PostgreSQL + PostGIS



\[ ] Add Object Storage (S3/MinIO) for FASTA/BAM/VCF files



\[ ] Integrate OpenSearch for full-text gene/genome search



\[ ] Add KEGG/COG annotation pipeline (eggNOG-mapper) for real-data genomes



\[ ] Add Nextflow pipelines for annotation, comparative genomics, and metagenomics



\[ ] Implement user authentication \& saved bookmarks/sessions



\[ ] Add genome comparison / synteny view



📜 License

Distributed under the MIT License. Free to use, modify, and distribute.



🙏 Acknowledgments

Genome annotation data sourced from NCBI Datasets API v2.



Inspired by the JBrowse 2 genome visualization architecture.

"""



with open("README.md", "w", encoding="utf-8") as f:

f.write(readme\_content)



print("README.md generated successfully.")





```text?code\_stdout\&code\_event\_index=1

README.md generated successfully.



Your Markdown file is ready



MD icon

README

&#x20;MD 

🌱 Plant Microbiome Genome Browser

A lightweight, full-stack genome browser for exploring plant-associated microbial genomes — annotations, GC content, tRNA/rRNA, mobile genetic elements, SNPs, metagenomic coverage, and comparative genomics — inspired by JBrowse 2 multi-track visualization.



Built with Flask + SQLite3 (backend/database) and a vanilla JS/Canvas frontend, designed to be swapped later for a production-grade React + JBrowse 2 UI and PostgreSQL + Object Storage backend.



✨ Features

🔍 Search \& Filter Genomes — Search by genome name, host plant, or environmental isolation source.



🧬 Multi-Track Genome Viewer — Render GC content, CDS/genes, tRNA/rRNA, mobile genetic elements, SNPs, and metagenomic coverage depth.



🖱️ Click-to-Inspect Genes — View detailed gene product, EC number, functional annotation, KEGG pathway, COG category, and expression data.



🌍 Environmental Metadata — Contextualize genomes with sample location, soil/tissue pH, ambient temperature, and isolation source.



🔬 Real NCBI-Sourced Annotations — Access 6 plant-associated microbial genomes fetched live via the NCBI Datasets API v2.



🧫 Curated Demo Genome — Includes Pseudomonas fluorescens Pf0-1 with hand-crafted annotation tracks matching reference genome browser specifications.



🔗 Comparative Genomics — Interactive cross-genome table linking orthologous genes across species.



🏗️ Architecture

Plaintext

Frontend (HTML/CSS/JS Canvas)

&#x20;     │

&#x20;     ▼

Flask REST API

&#x20;     │

&#x20;     ▼

SQLite3 Database

&#x20; ├── genomes

&#x20; ├── genes (CDS)

&#x20; ├── rna\_features (tRNA/rRNA)

&#x20; ├── kegg\_pathways

&#x20; ├── cog\_categories

&#x20; ├── mobile\_elements

&#x20; ├── snps

&#x20; ├── gc\_windows

&#x20; ├── coverage

&#x20; ├── expression

&#x20; ├── comparative\_genomics

&#x20; └── environmental\_metadata

Target Architecture: Designed to scale toward a React + TypeScript + JBrowse 2 frontend, Django / FastAPI microservices backend, PostgreSQL + PostGIS database, Object Storage (S3/MinIO) for FASTA/BAM/VCF alignment files, and OpenSearch for full-text gene indexing — matching production-grade metagenomics research platforms.



📂 Project Structure

Plaintext

Genome\_browser/

│

├── main.py                   # Flask app \& REST API routes

├── database.py               # SQLite connection helpers \& schema init

├── schema.sql                # Full database schema (12 tables)

├── seed\_data.py              # Seeds demo + curated real-gene data

├── fetch\_ncbi\_annotations.py # Pulls live GFF3 annotations from NCBI Datasets API

├── requirements.txt          # Python dependencies

├── .gitignore                # Git ignore rules

├── README.md                 # Project documentation

│

└── static/

&#x20;   ├── index.html            # Main UI layout

&#x20;   ├── style.css             # Application styling

&#x20;   └── app.js                # Canvas-based genome track renderer \& API integration

🚀 Getting Started

Prerequisites

Python 3.10 – 3.12 recommended (Python 3.14 works, but avoid packages requiring Rust/C compilation)



pip package manager



Step-by-Step Installation

1\. Clone the repository

Bash

git clone https://github.com/<your-username>/plant-microbiome-genome-browser.git

cd plant-microbiome-genome-browser

2\. Create and activate a virtual environment

Bash

\# Create virtual environment

python -m venv venv



\# Windows (PowerShell)

.\\venv\\Scripts\\Activate.ps1



\# macOS / Linux

source venv/bin/activate

3\. Install dependencies

Bash

pip install -r requirements.txt

4\. Seed the database

Bash

python seed\_data.py

5\. (Optional) Fetch live annotation data from NCBI

Bash

python fetch\_ncbi\_annotations.py

Note: Requires internet access. Pulls live GFF3 annotation data for all genome accessions stored in the database.



6\. Launch the application

Bash

python main.py

Open your browser and navigate to:

http://localhost:8000



🧬 Included Genomes

Genome	Host Plant	Environment	Assembly Accession

Pseudomonas fluorescens Pf0-1	Arabidopsis thaliana	Rhizosphere	GCF\_000007765.2

Bacillus velezensis FZB42	Arabidopsis thaliana	Rhizosphere	GCF\_000015785.2

Streptomyces griseus	Arabidopsis thaliana	Rhizosphere	GCF\_000009765.1

Pseudomonas putida KT2440	Zea mays	Rhizosphere	GCF\_000007565.2

Burkholderia phytofirmans PsJN	Oryza sativa	Endosphere	GCF\_000020125.1

Methylobacterium extorquens PA1	Solanum lycopersicum	Phyllosphere	GCF\_000018345.1

Streptomyces coelicolor A3(2)	—	Bulk Soil	GCF\_000203835.1

🔌 API Endpoints

Method	Endpoint	Description

GET	/api/genomes	List, search, or filter genomes

GET	/api/genomes/<id>	Fetch genome details + environmental metadata

GET	/api/genomes/<id>/genes?start=\&end=	Retrieve CDS/gene features in a specified genomic region

GET	/api/genomes/<id>/rna?start=\&end=	Retrieve tRNA/rRNA features in a region

GET	/api/genomes/<id>/mobile\_elements	Get mobile genetic elements in a region

GET	/api/genomes/<id>/snps	Query SNP / variant positions in a region

GET	/api/genomes/<id>/gc	Fetch GC content windows

GET	/api/genomes/<id>/coverage	Retrieve metagenomic read coverage depth

GET	/api/genomes/<id>/first\_genes	Get first annotated genes (used for auto-navigation)

GET	/api/genes/<id>	Full gene detail: product, KEGG, COG, expression

GET	/api/search?q=	Full-text search across gene names and products

GET	/api/genomes/<id>/comparative	Comparative genomics \& ortholog links

🛣️ Roadmap

\[ ] Replace Canvas renderer with real JBrowse 2 React component



\[ ] Migrate SQLite → PostgreSQL + PostGIS



\[ ] Add Object Storage (S3/MinIO) for FASTA/BAM/VCF files



\[ ] Integrate OpenSearch for full-text gene/genome search



\[ ] Add KEGG/COG annotation pipeline (eggNOG-mapper) for real-data genomes



\[ ] Add Nextflow pipelines for annotation, comparative genomics, and metagenomics



\[ ] Implement user authentication \& saved bookmarks/sessions



\[ ] Add genome comparison / synteny view



📜 License

Distributed under the MIT License. Free to use, modify, and distribute.



🙏 Acknowledgments

Genome annotation data sourced from NCBI Datasets API v2.



Inspired by the JBrowse 2 genome visualization architecture.



Pro is in high demand right now

Another model was used for this response. This didn't count toward your limit.







Gemini is AI and can make mistakes, including about people. Your privacy \& GeminiOpens in a new window



Integrating the Roadmap

\# 🌱 Plant Microbiome Genome Browser



> A lightweight, full-stack genome browser for exploring plant-associated microbial genomes — annotations, GC content, tRNA/rRNA, mobile genetic elements, SNPs, metagenomic coverage, and comparative genomics — inspired by JBrowse 2 multi-track visualization.



Built with \*\*Flask + SQLite3\*\* (backend/database) and a \*\*vanilla JS/Canvas\*\* frontend, designed to be swapped later for a production-grade \*\*React + JBrowse 2\*\* UI and \*\*PostgreSQL + Object Storage\*\* backend.



\---



\## ✨ Features



\- 🔍 \*\*Search \& Filter Genomes\*\* — Search by genome name, host plant, or environmental isolation source.

\- 🧬 \*\*Multi-Track Genome Viewer\*\* — Render GC content, CDS/genes, tRNA/rRNA, mobile genetic elements, SNPs, and metagenomic coverage depth.

\- 🖱️ \*\*Click-to-Inspect Genes\*\* — View detailed gene product, EC number, functional annotation, KEGG pathway, COG category, and expression data.

\- 🌍 \*\*Environmental Metadata\*\* — Contextualize genomes with sample location, soil/tissue pH, ambient temperature, and isolation source.

\- 🔬 \*\*Real NCBI-Sourced Annotations\*\* — Access 6 plant-associated microbial genomes fetched live via the NCBI Datasets API v2.

\- 🧫 \*\*Curated Demo Genome\*\* — Includes \*Pseudomonas fluorescens\* Pf0-1 with hand-crafted annotation tracks matching reference genome browser specifications.

\- 🔗 \*\*Comparative Genomics\*\* — Interactive cross-genome table linking orthologous genes across species.



\---



\## 🏗️ Architecture



```text

Frontend (HTML/CSS/JS Canvas)

&#x20;     │

&#x20;     ▼

Flask REST API

&#x20;     │

&#x20;     ▼

SQLite3 Database

&#x20; ├── genomes

&#x20; ├── genes (CDS)

&#x20; ├── rna\_features (tRNA/rRNA)

&#x20; ├── kegg\_pathways

&#x20; ├── cog\_categories

&#x20; ├── mobile\_elements

&#x20; ├── snps

&#x20; ├── gc\_windows

&#x20; ├── coverage

&#x20; ├── expression

&#x20; ├── comparative\_genomics

&#x20; └── environmental\_metadata

```



> \*\*Target Architecture:\*\* Designed to scale toward a \*\*React + TypeScript + JBrowse 2\*\* frontend, \*\*Django / FastAPI\*\* microservices backend, \*\*PostgreSQL + PostGIS\*\* database, \*\*Object Storage (S3/MinIO)\*\* for FASTA/BAM/VCF alignment files, and \*\*OpenSearch\*\* for full-text gene indexing — matching production-grade metagenomics research platforms.



\---



\## 📂 Project Structure



```text

Genome\_browser/

│

├── main.py                   # Flask app \& REST API routes

├── database.py               # SQLite connection helpers \& schema init

├── schema.sql                # Full database schema (12 tables)

├── seed\_data.py              # Seeds demo + curated real-gene data

├── fetch\_ncbi\_annotations.py # Pulls live GFF3 annotations from NCBI Datasets API

├── requirements.txt          # Python dependencies

├── .gitignore                # Git ignore rules

├── README.md                 # Project documentation

│

└── static/

&#x20;   ├── index.html            # Main UI layout

&#x20;   ├── style.css             # Application styling

&#x20;   └── app.js                # Canvas-based genome track renderer \& API integration

```



\---



\## 🚀 Getting Started



\### Prerequisites



\- \*\*Python 3.10 – 3.12\*\* recommended \*(Python 3.14 works, but avoid packages requiring Rust/C compilation)\*

\- \*\*pip\*\* package manager



\---



\### Step-by-Step Installation



\#### 1. Clone the repository

```bash

git clone https://github.com/<your-username>/plant-microbiome-genome-browser.git

cd plant-microbiome-genome-browser

```



\#### 2. Create and activate a virtual environment

```bash

\# Create virtual environment

python -m venv venv



\# Windows (PowerShell)

.\\venv\\Scripts\\Activate.ps1



\# macOS / Linux

source venv/bin/activate

```



\#### 3. Install dependencies

```bash

pip install -r requirements.txt

```



\#### 4. Seed the database

```bash

python seed\_data.py

```



\#### 5. (Optional) Fetch live annotation data from NCBI

```bash

python fetch\_ncbi\_annotations.py

```

> \*Note: Requires internet access. Pulls live GFF3 annotation data for all genome accessions stored in the database.\*



\#### 6. Launch the application

```bash

python main.py

```



Open your browser and navigate to:

\[http://localhost:8000](http://localhost:8000)



\---



\## 🧬 Included Genomes



| Genome | Host Plant | Environment | Assembly Accession |

| :--- | :--- | :--- | :--- |

| \*Pseudomonas fluorescens\* Pf0-1 | \*Arabidopsis thaliana\* | Rhizosphere | `GCF\_000007765.2` |

| \*Bacillus velezensis\* FZB42 | \*Arabidopsis thaliana\* | Rhizosphere | `GCF\_000015785.2` |

| \*Streptomyces griseus\* | \*Arabidopsis thaliana\* | Rhizosphere | `GCF\_000009765.1` |

| \*Pseudomonas putida\* KT2440 | \*Zea mays\* | Rhizosphere | `GCF\_000007565.2` |

| \*Burkholderia phytofirmans\* PsJN | \*Oryza sativa\* | Endosphere | `GCF\_000020125.1` |

| \*Methylobacterium extorquens\* PA1 | \*Solanum lycopersicum\* | Phyllosphere | `GCF\_000018345.1` |

| \*Streptomyces coelicolor\* A3(2) | — | Bulk Soil | `GCF\_000203835.1` |



\---



\## 🔌 API Endpoints



| Method | Endpoint | Description |

| :--- | :--- | :--- |

| `GET` | `/api/genomes` | List, search, or filter genomes |

| `GET` | `/api/genomes/<id>` | Fetch genome details + environmental metadata |

| `GET` | `/api/genomes/<id>/genes?start=\&end=` | Retrieve CDS/gene features in a specified genomic region |

| `GET` | `/api/genomes/<id>/rna?start=\&end=` | Retrieve tRNA/rRNA features in a region |

| `GET` | `/api/genomes/<id>/mobile\_elements` | Get mobile genetic elements in a region |

| `GET` | `/api/genomes/<id>/snps` | Query SNP / variant positions in a region |

| `GET` | `/api/genomes/<id>/gc` | Fetch GC content windows |

| `GET` | `/api/genomes/<id>/coverage` | Retrieve metagenomic read coverage depth |

| `GET` | `/api/genomes/<id>/first\_genes` | Get first annotated genes (used for auto-navigation) |

| `GET` | `/api/genes/<id>` | Full gene detail: product, KEGG, COG, expression |

| `GET` | `/api/search?q=` | Full-text search across gene names and products |

| `GET` | `/api/genomes/<id>/comparative` | Comparative genomics \& ortholog links |



\---



\## 📜 License



Distributed under the \*\*MIT License\*\*. Free to use, modify, and distribute.



\---



\## 🙏 Acknowledgments



\- Genome annotation data sourced from \*\*NCBI Datasets API v2\*\*.

\- Inspired by the \*\*JBrowse 2\*\* genome visualization architecture.



