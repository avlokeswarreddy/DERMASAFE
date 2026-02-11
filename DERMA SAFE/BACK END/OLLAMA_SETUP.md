# Ollama Setup Guide for DermaSafe

## What is Ollama?

Ollama is a local LLM (Large Language Model) runtime that allows you to run AI models like Llama 3 on your own computer without needing internet or cloud services.

## Current Status

✅ **Good News**: Your DermaSafe application will work even WITHOUT Ollama!
- The system automatically falls back to template-based responses
- Product analysis will still function correctly
- You'll see warnings in the console but everything will work

⚡ **Better with Ollama**: If you install Ollama, you'll get:
- AI-generated ingredient predictions for unknown products
- Natural, personalized dermatologist explanations
- More intelligent and context-aware responses

## How to Install Ollama (Optional but Recommended)

### Step 1: Download Ollama

1. Visit: https://ollama.com/download
2. Download the Windows installer
3. Run the installer and follow the prompts

### Step 2: Install the Llama3 Model

After installing Ollama, open **PowerShell** or **Command Prompt** and run:

```bash
ollama pull llama3
```

This will download the Llama 3 model (about 4.7 GB). It may take a few minutes depending on your internet speed.

### Step 3: Verify Installation

Run the test script to verify everything is working:

```bash
python test_ollama.py
```

You should see:
```
✅ Ollama is available with llama3 model
Response received: [AI response]
```

### Step 4: Start Your Backend

Once Ollama is installed and running, start your DermaSafe backend:

```bash
python app.py
```

You should see in the logs:
```
INFO:__main__:Checking Ollama availability...
INFO:__main__:✅ Ollama is available with llama3 model
```

## Troubleshooting

### "Ollama not available" Warning

**Symptoms**: You see `⚠️ Ollama not available: ...` in the console

**Solutions**:
1. **Check if Ollama is running**: 
   - On Windows, Ollama should start automatically after installation
   - Look for the Ollama icon in your system tray
   - If not running, search for "Ollama" in Start Menu and launch it

2. **Verify the model is installed**:
   ```bash
   ollama list
   ```
   You should see `llama3` in the list. If not, run:
   ```bash
   ollama pull llama3
   ```

3. **Test Ollama directly**:
   ```bash
   ollama run llama3 "Hello"
   ```
   If this works, Ollama is running correctly.

### Port Conflicts

Ollama runs on port 11434 by default. If you have another service using this port, you may need to stop it or configure Ollama to use a different port.

### Model Not Found

If you see "llama3 model NOT found", make sure you've pulled the model:
```bash
ollama pull llama3
```

## System Requirements for Ollama

- **RAM**: At least 8 GB (16 GB recommended)
- **Disk Space**: ~5 GB for the llama3 model
- **OS**: Windows 10/11, macOS, or Linux

## Using DermaSafe Without Ollama

If you choose not to install Ollama or it's not available:

1. The application will automatically use fallback mode
2. You'll see warnings like: `⚠️ Ollama not available. Using fallback mode.`
3. **Everything will still work!** The analysis will use:
   - Pattern-based ingredient prediction
   - Template-based explanations
   - All safety analysis features remain functional

## Performance Comparison

| Feature | With Ollama | Without Ollama |
|---------|-------------|----------------|
| Product Analysis | ✅ AI-powered | ✅ Pattern-based |
| Ingredient Detection | ✅ Intelligent | ✅ Keyword matching |
| Explanations | ✅ Natural language | ✅ Templates |
| Speed | ~2-5 seconds | ~instant |
| Accuracy | Higher | Good |
| Offline | ✅ Yes | ✅ Yes |

## Recommended Setup

For the best experience:

1. ✅ Install Ollama
2. ✅ Pull the llama3 model
3. ✅ Keep Ollama running in the background
4. ✅ Start your DermaSafe backend

The system will automatically detect and use Ollama when available!
