import sys
sys.path.append('..')

try:
    # New package location (preferred)
    from langchain_perplexity import ChatPerplexity
except Exception:
    # Fallback to older (deprecated) location if available in this environment
    from langchain_community.chat_models import ChatPerplexity
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def test_perplexity_llm():
    """Test Perplexity LLM"""
    print("🔍 Testing Perplexity LLM...")
    # Allow configuring the model through an environment variable so users can
    # choose a supported Perplexity model without editing the test.
    model = os.getenv('PERPLEXITY_MODEL')
    if not model:
        print("⚠️  PERPLEXITY_MODEL not set — skipping Perplexity model test.\n"
              "Set PERPLEXITY_MODEL in your .env to a supported model (see Perplexity docs).")
        return None

    try:
        llm = ChatPerplexity(
            model=model,
            temperature=0.2,
            pplx_api_key=os.getenv('PERPLEXITY_API_KEY'),
            max_tokens=1024
        )

        response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
        print(f"✅ Perplexity LLM working!")
        print(f"💬 Response: {response.content}")
        return True
    except Exception as e:
        # Surface the raw error but add guidance for the common invalid-model case.
        msg = str(e)
        print(f"❌ Perplexity LLM failed: {msg}")
        if 'invalid_model' in msg or 'Invalid model' in msg:
            print("💡 Tip: The model you requested is invalid or not permitted by the Perplexity API."
                  " Set PERPLEXITY_MODEL to a supported model name (check Perplexity docs) or"
                  " remove the Perplexity test if you don't have access to a supported model.")
        else:
            print("💡 Tip: Check if PERPLEXITY_API_KEY is set in .env and is valid.")
        return False

def test_groq_llm():
    """Test Groq LLM (alternative)"""
    print("\n🔍 Testing Groq LLM...")
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv('GROQ_API_KEY'),
            temperature=0.7
        )
        
        response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
        print(f"✅ Groq LLM working!")
        print(f"💬 Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Groq LLM failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_perplexity_llm()
    test_groq_llm()
