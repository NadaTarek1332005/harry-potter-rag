# Harry Potter RAG System

A Retrieval-Augmented Generation (RAG) chatbot built using the Harry Potter books as a knowledge base.

## Features

- Query routing (Retrieve, Chitchat, Off-topic)
- Semantic retrieval using Qdrant
- Answer generation with Gemini
- Source attribution with page numbers
- Confidence score display
- Retrieval evaluation using Precision, Recall, and F1 Score
- LLM-as-a-Judge evaluation
- FastAPI backend
- Interactive web interface

## Tech Stack

- FastAPI
- Qdrant
- Sentence Transformers
- Gemini
- Groq
- HTML
- CSS
- JavaScript

## Project Structure

```text
harry-potter-rag/
│
├── data/
│   └── harrypotter.pdf
│
├── notebook/
│   └── data_preparation.ipynb
│
├── screenshots/
│   ├── retrieval-horcrux.png
│   ├── retrieval-sirius-black.png
│   ├── retrieval-dark-forces.png
│   ├── chitchat-route.png
│   └── off-topic-route.png
│
├── ui/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── rag_api.py
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## RAG Pipeline

1. Parse the Harry Potter PDF document.
2. Convert the PDF into Markdown.
3. Clean and preprocess the text.
4. Split the books into page-level chunks.
5. Generate embeddings using Sentence Transformers.
6. Store embeddings in Qdrant.
7. Route incoming queries.
8. Retrieve relevant pages.
9. Generate grounded answers from the retrieved context.
10. Return the answer, sources, and confidence score.

## Evaluation

The retrieval system is evaluated using:

- Precision
- Recall
- F1 Score

The generated answers are additionally evaluated using:

- LLM-as-a-Judge
- Grounding assessment
- Answer quality scoring

## Enhancements

The following improvements were added beyond the baseline implementation:

- Added F1 Score to retrieval evaluation.
- Added a dedicated Judge Model for answer evaluation.
- Added confidence scores to API responses and UI.
- Added source relevance scores to the UI.
- Improved prompts to reduce hallucinations.
- Added page citations in generated answers.
- Improved answer grounding using retrieved context.

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=

EMBEDDING_MODEL=intfloat/multilingual-e5-large

GEMINI_MODEL=
GEMINI_API_KEY=

GROQ_MODEL=
GROQ_API_KEY=

TOP_K=3
```

## Running the API

```bash
python -m uvicorn rag_api:app --reload
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

## UI Features

- Ask questions in natural language.
- View generated answers.
- View retrieved sources.
- View retrieval confidence scores.
- Check server health directly from the interface.

## Screenshots

### Retrieval Example 1 - Sirius Black

![Retrieval Sirius Black](https://github.com/NadaTarek1332005/harry-potter-rag/blob/b5713323347e68c84dd0bb8015c98984bf90d12f/Harry-Potter-RAG/screenshots/retrieval-sirius-black.jpg)

### Retrieval Example 2 - Horcrux

![Retrieval Horcrux](https://github.com/NadaTarek1332005/harry-potter-rag/blob/355f95515005232687eb87da86a7e17ed611cce2/Harry-Potter-RAG/screenshots/retrieval-horcrux.jpg)

### Retrieval Example 3 - Dark Forces

![Retrieval Dark Forces](https://github.com/NadaTarek1332005/harry-potter-rag/blob/355f95515005232687eb87da86a7e17ed611cce2/Harry-Potter-RAG/screenshots/retrieval-dark-forces.jpg)

### Off-topic Route

![Off-topic Route](https://github.com/NadaTarek1332005/harry-potter-rag/blob/d3f46d702d9560749f67546e6bc569b9142050e3/Harry-Potter-RAG/screenshots/off-topic-route.jpg)

### Chitchat Route

![Chitchat Route](https://github.com/NadaTarek1332005/harry-potter-rag/blob/d3f46d702d9560749f67546e6bc569b9142050e3/Harry-Potter-RAG/screenshots/chitchat-route.jpg)

## Author

Nada Tarek Mostafa
