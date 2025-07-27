# REAL ESTATE REASERCH ASSISTANT
A production-ready AI-powered research tool for real estate professionals, investors, and enthusiasts. Extract insights from web articles, reports, and documents using advanced RAG (Retrieval Augmented Generation) technology.

## Core Capabilities

* 📥 Multi-URL Processing: Load content from multiple web sources simultaneously
* 🔍 Intelligent Search: Ask natural language questions about processed content
* 📊 Source Attribution: Get answers with proper source citations
* ⚡ Real-time Processing: Live status updates during data processing
* 🏗️ Production Ready: Enterprise-grade architecture with proper error handling

## Technical Features

1. 🤖 AI-Powered: Uses Llama 3.3 via Groq for answer generation
2. 🧠 Vector Search: ChromaDB with HuggingFace embeddings for semantic search
3. 🔒 Security: Input validation, sanitization, and rate limiting
4. 📈 Monitoring: Health checks, logging, and performance metrics
5. 🐳 Containerized: Docker support for easy deployment
6. 🧪 Tested: Comprehensive unit and integration tests

## Installation

1. **Clone the repository**:

```
git clone https://github.com/lintosunny/Real-Estate-Research-Assistant.git
```

2. **Create and activate a virtual environment (optional but recommended)**:

```
conda create -n env python=3.10 -y
```

```
conda activate env
```

3. **Install Dependencies**:

```
pip install -r requirements.txt
```

4. **Setup your API Key**:

Create a ```.env``` file in the root directory and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the App**
```
streamlit run main.py
```
Once started app will be open in your default web browser.


