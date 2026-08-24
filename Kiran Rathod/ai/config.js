/**
 * Construction Intelligent Hub (CIH) - Ollama AI Configuration
 * 
 * Modular configuration for the local offline AI runtime.
 * Default Primary Model: Llama 3.2 (llama3.2)
 * Extensible for any Ollama supported model (llama3.2, deepseek-r1, mistral, codellama).
 */

const OLLAMA_CONFIG = {
    // Local Ollama API daemon endpoint
    endpoint: "http://localhost:11434",
    ollamaBaseUrl: "http://localhost:11434",
    
    // Active & Default Ollama model name (Llama 3.2 is primary default)
    model: "llama3.2",
    defaultModel: "llama3.2",
    activeModel: "llama3.2",

    // Priority model fallback list with llama3.2 as #1 priority
    priorityModels: ["llama3.2", "mistral", "deepseek-r1", "codellama"],
    fallbackModels: ["llama3.2", "mistral", "deepseek-r1", "codellama"],
    
    // Model inference parameters optimized for Llama 3.2
    options: {
        temperature: 0.4,
        top_p: 0.9,
        num_predict: 450
    },

    // Response streaming toggle
    stream: false,

    // Intelligent dynamic fallback when Ollama service is offline
    fallbackEnabled: true,
    
    // Timeout for AI inference HTTP requests (90 seconds to allow full Llama 3.2 completion on local hardware)
    timeoutMs: 90000,

    // Timeout for health check endpoint (1.5 seconds)
    healthCheckTimeoutMs: 1500
};
