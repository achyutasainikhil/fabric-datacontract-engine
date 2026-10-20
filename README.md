# 🛡️ Fabric Data Contract Engine & Quality Governance POC

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-Delta%20Lake-orange)](https://spark.apache.org/)
[![Soda Core](https://img.shields.io/badge/Soda-Data%20Quality-green)](https://www.soda.io/)
[![Microsoft Fabric](https://img.shields.io/badge/Microsoft-Fabric-purple)](https://www.microsoft.com/en-us/microsoft-fabric)

An enterprise-grade **Data Contract CLI & Quality Governance Engine** built with **PySpark** and **Soda Core**. This Proof of Concept (POC) implements a core pillar of **Data Mesh** architecture: treating data as a product by enforcing strict declarative contracts, schema validations, custom SQL business rules, and automated quality scans *before* datasets reach downstream consumers.

---

## 🎯 Project Goal & Business Value
In modern data ecosystems, data corruption often goes unnoticed until it pollutes production dashboards or machine learning models. The goal of this project is to implement **Shift-Left Data Quality Governance** by introducing **Contract-as-Code**. 

Rather than relying on manual checks or centralized IT intervention, domain teams publish data products governed by automated guardrails that:
1. **Prevent Breaking Changes:** Instantly catch dropped, added, or renamed columns.
2. **Enforce Business Rules:** Guarantee domain constraints (e.g., zero negative tenure months).
3. **Automate Data Quality Scans:** Check for missing values, uniqueness constraints, and numeric ranges using open-source tools like Soda Core.
4. **Fail-Fast Guardrails:** Automatically block malformed data products from polluting enterprise storage layers.

---

## 📊 Dataset Used
* **Dataset Name:** IBM Telco Customer Churn Dataset
* **Source:** Publicly hosted sample dataset tracking customer demographics, account info, tenure, and churn status.
* **Usage in Pipeline:** Ingested via PySpark, standardized into clean column schemas, and loaded into enterprise Delta tables representing our domain's Gold Layer (`gold_customer_churn`).

---

## 🏗️ Architecture & Workflow

<img width="909" height="326" alt="image" src="https://github.com/user-attachments/assets/1231f925-a57b-4735-b017-f9ec4335619f" />


---

## 🚀 Repository Structure

```text
fabric-datacontract-engine/
├── README.md                 # Project documentation & architecture overview
├── requirements.txt          # Python dependencies
├── datacontract.yaml         # Declarative schema and quality rules
└── main.py                   # Ingestion, validation CLI class, and demo runner

💻 Quick Start (Local Execution)

1. Clone the Repository

git clone [https://github.com/YOUR_GITHUB_USERNAME/fabric-datacontract-engine.git](https://github.com/YOUR_GITHUB_USERNAME/fabric-datacontract-engine.git)
cd fabric-datacontract-engine

2. Install Dependencies

pip install -r requirements.txt

3. Run the Validation Demo
Execute the main script to see both a successful pristine data run and an intentional guardrail failure block live in your terminal:

python main.py

☁️ How to Deploy & Run in Microsoft Fabric
While this POC can run locally on PySpark, it is natively designed to integrate into Microsoft Fabric notebooks and pipelines:

Upload Artifacts to Lakehouse:

Upload your datacontract.yaml file into your Fabric Lakehouse under Files/datacontract.yaml.

Install Libraries in Spark Environment:

In your Fabric Workspace settings or notebook environment configuration, add soda-core, soda-core-spark, and pyyaml to your workspace libraries.

Run via Fabric Notebooks:

Load your gold Delta tables using spark.table("gold_customer_churn").

Initialize the FabricDataContractCLI class referencing your Lakehouse contract path (/lakehouse/default/Files/datacontract.yaml).

Automate via Data Factory:

Chain the validation script into a Fabric Data Factory pipeline activity. If validation fails and throws an exception, the pipeline halts automatically, ensuring data reliability.
