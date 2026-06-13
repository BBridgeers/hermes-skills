---
name: dynamic-openrouter-model-routing
description: Routes files to appropriate OpenRouter models based on extension for ingestion with batch processing and rate limiting
---
# Dynamic OpenRouter Model Routing for File Ingestion

This skill provides a Python function that routes files to appropriate OpenRouter models based on file extension:
- Text files (.txt, .md, .py, .cpp, .json, .csv, etc.) → nvidia/nemotron-3-super-120b-a12b:free (processed in batch)
- Image files (.png, .jpg, .jpeg) → google/gemma-4-31b-it:free with multimodal payload (rate-limited)
- Binary hardware files (.stl, .step, .brd, .zip, etc.) → skipped with log

The function `process_directory_for_openrouter` processes directories efficiently by:
1. Batching all text files into a single API call to reduce requests
2. Rate-limiting image processing to stay under OpenRouter's free tier limits
3. Applying a system prompt to guide the analysis

## Usage

```python
from scripts.route_openrouter import process_directory_for_openrouter
results = process_directory_for_openrouter(
    "/path/to/directory", 
    api_key="your-openrouter-key",
    system_prompt="Your analysis prompt here"
)
print(results)
```

## Requirements

- Python 3.8+
- requests library (`pip install requests`)

## Lessons Learned & Best Practices

Based on practical usage:

1. **Model Name Accuracy**: Always verify the exact model ID on OpenRouter (e.g., use `nvidia/nemotron-3-super-120b-a12b:free` not `nvidia/nemotron-3-super-free`).

2. **Rate Limit Management**: 
   - Free tier OpenRouter models have strict limits (e.g., 20 requests/minute for Gemma)
   - Implement `time.sleep(4)` between image API calls to stay safely under limits
   - Batch text processing reduces requests from N to 1, drastically lowering rate limit risk

3. **Timeout Prevention**:
   - Large master contexts can cause timeouts; truncate individual file content (e.g., 800-2000 chars per file)
   - Limit the number of files processed in a single run when dealing with large codebases
   - Process files by modification time to focus on the most relevant/recent files

4. **Error Handling**:
   - Always check for API errors (status codes 429, 400, etc.) before parsing responses
   - Provide fallbacks for MIME type detection
   - Skip unreadable binary files explicitly to prevent garbage data

5. **Architectural Overrides**:
   - Use specific system prompts to guide the analysis toward desired interpretations
   - Can be used to ignore legacy files or focus on specific technical aspects
   - Combine with file filtering (by date, path, or content) for targeted analysis

6. **Iterative Approach**:
   - Start with small file samples to validate the approach
   - Gradually increase scope as confidence grows
   - Save intermediate results to avoid reprocessing