# CinematicAI: Intelligent Movie Recommendation Assistant

CinematicAI is an advanced movie recommendation system that leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide personalized movie recommendations. The system analyzes user preferences, movie reviews, and metadata to deliver contextually relevant and detailed movie suggestions.

## 🎬 Features

- **Natural Language Interface**: Conversational movie recommendations through a chat-like interface
- **Personalized Recommendations**: Tailored suggestions based on preferences, genres, actors, directors, and more
- **Contextual Memory**: Maintains conversation history to provide coherent follow-up recommendations
- **Detailed Movie Information**: Provides ratings, genres, cast information, and reviewer sentiments
- **Hybrid Retrieval System**: Combines BM25 and vector-based search for effective information retrieval
- **Review Analysis**: Leverages actual user reviews to provide nuanced recommendation reasoning

## 🛠️ Technologies

- **LLM**: Microsoft Phi-3-mini-4k-instruct
- **Embedding Model**: sentence-transformers/all-mpnet-base-v2
- **Re-ranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Vector Database**: Pinecone
- **Information Retrieval**: BM25 + Dense Vector Retrieval
- **Data Processing**: Python, Pandas, Torch
- **Data Collection**: Selenium, Beautiful Soup

## 📊 Data Sources

The system uses:
- Movie metadata (titles, genres, ratings, directors, cast)
- User reviews scraped from IMDb
- Processing includes chunking, embedding, and indexing for efficient retrieval

## 🚀 Implementation

The system implements a RAG (Retrieval-Augmented Generation) pipeline:

1. **Query Processing**: Analyzes user requests to understand preferences and constraints
2. **Hybrid Retrieval**: Combines sparse (BM25) and dense (vector) retrieval to find relevant movie information and reviews
3. **Re-ranking**: Scores and prioritizes retrieved chunks based on relevance
4. **Context Building**: Constructs a comprehensive prompt with the most relevant information
5. **Response Generation**: Uses the LLM to generate natural, coherent recommendations

## 📁 Repository Structure

- `Cinematic_AI_Assistant_sample.ipynb`: Sample of the main notebook implementation
- `webscrapping.py`: Script for data collection from IMDb
- `requirements.txt`: Python dependencies
- `LARGE_FILES.md`: Information about large files not included in the repository

**Note**: Due to GitHub file size limitations, some files are not included in this repository. See [LARGE_FILES.md](LARGE_FILES.md) for more information.

## 📋 Setup Instructions

1. **Environment Setup**:
   ```python
   pip install -r requirements.txt
   ```

2. **Configuration**:
   ```python
   CONFIG = {
       # Core components
       "index_name": "movie-rag-index",
       "embedding_model": "sentence-transformers/all-mpnet-base-v2",
       "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2",
       "llm_model": "microsoft/Phi-3-mini-4k-instruct",

       # Processing parameters
       "chunk_size": 600,
       "chunk_overlap": 100,
       "top_k_retrieve": 50,
       "top_k_final": 12,

       # Response generation
       "max_response_tokens": 800,
       "min_imdb_rating": 6.5,
       "default_year_range": 10,
   }
   ```

3. **Data Collection** (optional, as dataset is provided):
   - Run the `webscrapping.py` script to collect additional movie data
   - Adjust parameters in the script for different movie selections

4. **Running the System**:
   - Follow the Jupyter notebook `Cinematic_AI_Assistant_sample.ipynb` for understanding the implementation structure
   - For the complete implementation, refer to the information in LARGE_FILES.md

## 💬 Example Queries

- "Can you recommend a sci-fi movie with themes similar to Blade Runner?"
- "I'm looking for comedies from the 90s with high ratings"
- "What are some good drama movies about family relationships directed by women?"
- "I enjoyed The Shawshank Redemption and The Green Mile. What should I watch next?"
- "Show me action movies with strong female leads made in the last 5 years"

## 🔄 Workflow Diagram

```
User Query → Query Analysis → Hybrid Retrieval → Re-ranking → Context Building → LLM Generation → Response
```

## 🧠 System Capabilities

1. **Understands Complex Preferences**: Processes nuanced requests combining genres, themes, actors, time periods
2. **Quality Filtering**: Prioritizes well-reviewed and higher-rated content
3. **Reasoning**: Explains why recommendations match user preferences
4. **Follow-up Handling**: Maintains context for multi-turn conversations
5. **Review Synthesis**: Incorporates actual viewer opinions into recommendations

## 👥 Contributors

- Filbert Hamijoyo

## 📄 License

This project is available for academic and personal use. Please respect the terms of service of any third-party data sources and models used in this project.

## 📚 References

- For more information on the techniques used, please refer to the comprehensive report in `Cinematic_AI_Assistant.pdf`