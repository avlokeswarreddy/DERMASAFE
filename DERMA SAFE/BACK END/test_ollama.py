import ollama
import sys

try:
    print("Checking Ollama connection...")
    models = ollama.list()
    print("Ollama is reachable.")
    print("Available models:")
    found_llama3 = False
    for m in models['models']:
        print(f" - {m['name']}")
        if 'llama3' in m['name']:
            found_llama3 = True
    
    if found_llama3:
        print("\nllama3 model found.")
        print("Attempting generation...")
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': 'Hello'}])
        print("Response received:", response['message']['content'])
    else:
        print("\nWARNING: llama3 model NOT found in the list.")

except Exception as e:
    print(f"\nERROR: Failed to connect to Ollama: {e}")
    sys.exit(1)
