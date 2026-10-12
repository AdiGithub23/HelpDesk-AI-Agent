# Documentation/Embeddings

---

## Embeddings

`gemini-embedding-001` is Google's text embedding model for RAG and semantic search, converting text into vector embeddings that help retrieve the most relevant information from a vector database before generating responses.

## Generating embeddings  {% id="generate-embeddings" %}

```py
from google import genai

client = genai.Client()

result = client.models.embed_content(
        model="gemini-embedding-2",
        contents="What is the meaning of life?"
)

print(result.embeddings)
```

## Specify task type to improve performance  {% id="task-types" %}

You can use embeddings for a wide range of tasks from classification to document search. Specifying the right task type helps optimize the embeddings for the intended relationships, maximizing accuracy and efficiency.

### Task types with Embeddings 1  {% id="task-types-embeddings-1" %}

For `gemini-embedding-001`, you can specify the `task_type` in the `embedContent` method. For a complete list of supported task types, see the
[Supported task types](/docs/embeddings#supported-task-types) table. This example shows how to use `SEMANTIC_SIMILARITY` to check how similar in meaning strings of texts are.

```python
from google import genai
from google.genai import types
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

client = genai.Client()

texts = [
    "What is the meaning of life?",
    "What is the purpose of existence?",
    "How do I bake a cake?",
]

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts,
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)

df = pd.DataFrame(
    cosine_similarity([e.values for e in result.embeddings]),
    index=texts,
    columns=texts,
)

print(df)
```

The code snippets will show how similar the different chunks of text are to one another when run.

#### Supported task types  {% id="supported-task-types" %}

Supported task types for `gemini-embedding-001`:

{% table %}
  * **SEMANTIC_SIMILARITY**
  * Embeddings optimized to assess text similarity.
  * Recommendation systems, duplicate detection

  ---

  * **CLASSIFICATION**
  * Embeddings optimized to classify texts according to preset labels.
  * Sentiment analysis, spam detection

  ---

  * **CLUSTERING**
  * Embeddings optimized to cluster texts based on their similarities.
  * Document organization, market research, anomaly detection

  ---

  * **RETRIEVAL_DOCUMENT**
  * Embeddings optimized for document search.
  * Indexing articles, books, or web pages for search.

  ---

  * **RETRIEVAL_QUERY**
  * Embeddings optimized for general search queries. Use `RETRIEVAL_QUERY` for
    queries; `RETRIEVAL_DOCUMENT` for documents to be retrieved.
  * Custom search

  ---

  * **CODE_RETRIEVAL_QUERY**
  * Embeddings optimized for retrieval of code blocks based on natural language
    queries. Use `CODE_RETRIEVAL_QUERY` for queries; `RETRIEVAL_DOCUMENT` for code
    blocks to be retrieved.
  * Code suggestions and search

  ---

  * **QUESTION_ANSWERING**
  * Embeddings for questions in a question-answering system, optimized for finding
    documents that answer the question. Use `QUESTION_ANSWERING` for questions;
    `RETRIEVAL_DOCUMENT` for documents to be retrieved.
  * Chatbox

  ---

  * **FACT_VERIFICATION**
  * Embeddings for statements that need to be verified, optimized for retrieving
    documents that contain evidence supporting or refuting the statement. Use
    `FACT_VERIFICATION` for the target text; `RETRIEVAL_DOCUMENT` for documents to
    be retrieved.
  * Automated fact-checking systems
{% /table %}

## Controlling embedding size  {% id="control-embedding-size" %}

Use the `output_dimensionality` parameter to control the size of the output embedding vector. We recommend using 768, 1536, or 3072 output dimensions.

```py
from google import genai
from google.genai import types

client = genai.Client()

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="What is the meaning of life?",
    config=types.EmbedContentConfig(output_dimensionality=768)
)

[embedding_obj] = result.embeddings
embedding_length = len(embedding_obj.values)

print(f"Length of embedding: {embedding_length}")
```

Example output from the code snippet:

```none
Length of embedding: 768
```

## Ensuring quality for smaller dimensions  {% id="quality-for-smaller-dimensions" %}

Default 3072-dimension embeddings are always normalized. For `gemini-embedding-001`, you must manually normalize non-3072 dimensions as follows:
```py
import numpy as np
from numpy.linalg import norm

embedding_values_np = np.array(embedding_obj.values)
normed_embedding = embedding_values_np / np.linalg.norm(embedding_values_np)

print(f"Normed embedding length: {len(normed_embedding)}")
print(f"Norm of normed embedding: {np.linalg.norm(normed_embedding):.6f}") # Should be very close to 1
```

Example output from this code snippet:
```none
Normed embedding length: 768
Norm of normed embedding: 1.000000
```

## Use cases  {% id="common-use-cases" %}

Text embeddings are crucial for a variety of common AI use cases, such as:

* **Retrieval-Augmented Generation (RAG):** Embeddings enhance the quality of generated text by retrieving and incorporating relevant information into the context of a model.

* **Information retrieval:** Search for the most semantically similar text or documents given a piece of input text.

  {% button href="https://github.com/google-gemini/cookbook/blob/main/examples/Talk_to_documents_with_embeddings.ipynb" icon="task" variant="primary" %}Document search tutorial{% /button %}

* **Search reranking**: Prioritize the most relevant items by semantically scoring initial results against the query.

  {% button href="https://github.com/google-gemini/cookbook/blob/main/examples/Search_reranking_using_embeddings.ipynb" icon="task" variant="primary" %}Search reranking tutorial{% /button %}
