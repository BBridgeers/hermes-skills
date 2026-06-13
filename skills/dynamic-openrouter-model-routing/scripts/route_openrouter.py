import os
import base64
import requests
import mimetypes
import time
from typing import Dict, Any, Optional, List

def process_file_for_openrouter(file_path: str, api_key: str) -> Dict[str, Any]:
    """
    Process a file for OpenRouter ingestion with dynamic model routing.
    
    Args:
        file_path: Path to the file to process
        api_key: OpenRouter API key
        
    Returns:
        Dictionary containing the API response or error information
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    # Get file extension in lowercase
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Define extension categories
    text_extensions = {'.txt', '.md', '.py', '.cpp', '.c', '.h', '.hpp', '.json', '.csv', '.tsv', '.xml', '.yaml', '.yml', '.html', '.htm', '.css', '.js', '.ts', '.java', '.rb', '.go', '.rs', '.sh', '.bash', '.zsh', '.fish', '.ini', '.cfg', '.conf', '.toml', '.log'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    binary_blacklist = {'.stl', '.step', '.stp', '.brd', '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.dll', '.so', '.bin', '.dat', '.obj', '.fbx', '.blend', '.max', '.dwg', '.dxf'}
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Text Pipeline
        if ext in text_extensions:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            payload = {
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        
        # Vision Pipeline
        elif ext in image_extensions:
            # Read and encode image
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = f"image/{ext[1:]}"  # fallback
            
            payload = {
                "model": "google/gemma-4-31b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this hardware design and describe how it functions."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        
        # PDF handling (special case - extract text or alert)
        elif ext == '.pdf':
            return {
                "warning": "PDF file detected. OpenRouter vision models require image input. "
                           "Consider converting PDF to PNG first for vision analysis, "
                           "or use a text extraction tool to get the content for text processing."
            }
        
        # Blacklist Pipeline
        elif ext in binary_blacklist:
            print(f"Skipped unreadable binary: {file_path}")
            return {"skipped": True, "reason": "Binary hardware format", "file": file_path}
        
        # Unknown extension
        else:
            return {
                "warning": f"Unknown file extension '{ext}'. File treated as text if readable, otherwise skipped.",
                "suggestion": "Add extension to appropriate category in the function."
            }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

def process_directory_for_openrouter(directory_path: str, api_key: str, system_prompt: str, recursive: bool = True) -> Dict[str, Any]:
    """
    Process all files in a directory with dynamic model routing.
    Implements batch text processing and rate-limited vision calls.

    Args:
        directory_path: Path to the directory to process
        api_key: OpenRouter API key
        system_prompt: System prompt to guide the analysis
        recursive: Whether to process subdirectories

    Returns:
        Dictionary containing combined analysis results
    """
    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}

    # Define extension categories
    text_extensions = {'.txt', '.md', '.py', '.cpp', '.c', '.h', '.hpp', '.json', '.csv', '.tsv', '.xml', '.yaml', '.yml', '.html', '.htm', '.css', '.js', '.ts', '.java', '.rb', '.go', '.rs', '.sh', '.bash', '.zsh', '.fish', '.ini', '.cfg', '.conf', '.toml', '.log'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    binary_blacklist = {'.stl', '.step', '.stp', '.brd', '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.dll', '.so', '.bin', '.dat', '.obj', '.fbx', '.blend', '.max', '.dwg', '.dxf'}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 1. BATCH TEXT PROCESSING - Collect all text content
    master_context = ""
    text_files_processed = []
    skipped_files = []
    errors = []

    print("Collecting text files for batch processing...")
    for root, dirs, files in os.walk(directory_path):
        # Skip hidden directories and common build/cache dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'Archive_Obsolete']]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory_path)
            _, ext = os.path.splitext(file)
            ext = ext.lower()

            if ext in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    master_context += f"\n--- FILE: {relative_path} ---\n{content}\n"
                    text_files_processed.append(relative_path)
                except Exception as e:
                    errors.append(f"Failed to read {relative_path}: {str(e)}")
            elif ext in binary_blacklist:
                print(f"Skipped unreadable binary: {relative_path}")
                skipped_files.append((relative_path, "Binary hardware format"))
            elif ext not in image_extensions and ext != '.pdf':
                # Track other extensions for info
                skipped_files.append((relative_path, f"Unknown extension '{ext}'"))

    # 2. SINGLE TEXT API CALL
    print(f"Processing {len(text_files_processed)} text files in a single batch...")
    text_result = {"skipped": skipped_files, "errors": errors}
    
    if master_context.strip():
        try:
            payload = {
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": master_context
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000  # Increased for comprehensive analysis
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            text_result["analysis"] = response.json()
        except requests.exceptions.RequestException as e:
            text_result["error"] = f"API request failed: {str(e)}"
        except Exception as e:
            text_result["error"] = f"Processing failed: {str(e)}"
    else:
        text_result["warning"] = "No text files found to process"

    # 3. RATE-LIMITED VISION PROCESSING
    print("Processing image files with rate limiting...")
    image_results = {}
    image_files_to_process = []
    
    for root, dirs, files in os.walk(directory_path):
        # Skip hidden directories and common build/cache dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'Archive_Obsolete']]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory_path)
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            if ext in image_extensions:
                image_files_to_process.append((file_path, relative_path))

    print(f"Found {len(image_files_to_process)} image files to process")
    
    for i, (file_path, relative_path) in enumerate(image_files_to_process):
        print(f"  [{i+1}/{len(image_files_to_process)}] Processing {relative_path}")
        
        try:
            # Read and encode image
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = f"image/{ext[1:]}"  # fallback
            
            payload = {
                "model": "google/gemma-4-31b-it:free",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this hardware design and describe how it functions."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            image_results[relative_path] = response.json()
            
            # Rate limiting: sleep 4 seconds between calls to stay under 20/minute
            if i < len(image_files_to_process) - 1:  # Don't sleep after the last file
                print(f"    Rate limiting: sleeping 4 seconds...")
                time.sleep(4)
                
        except requests.exceptions.RequestException as e:
            image_results[relative_path] = {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            image_results[relative_path] = {"error": f"Processing failed: {str(e)}"}

    # 4. RETURN UNIFIED RESULTS
    return {
        "text_analysis": text_result,
        "image_analyses": image_results,
        "summary": {
            "text_files_processed": len(text_files_processed),
            "image_files_processed": len(image_files_to_process),
            "skipped_files": len(skipped_files),
            "errors": len(errors)
        }
    }

# Example usage (uncomment to test)
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) != 3:
#         print("Usage: python route_openrouter.py <file_or_directory> <api_key>")
#         sys.exit(1)
#     
#     target = sys.argv[1]
#     api_key = sys.argv[2]
#     
#     if os.path.isfile(target):
#         result = process_file_for_openrouter(target, api_key)
#         print(result)
#     elif os.path.isdir(target):
#         results = process_directory_for_openrouter(target, api_key)
#         for file_path, result in results.items():
#             print(f"\n--- {file_path} ---")
#             print(result)
#     else:
#         print(f"Target not found: {target}")