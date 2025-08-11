from typing import List, Dict, Any
import re
from pygments import lexers
from pygments.util import ClassNotFound

def extract_code_snippets(text: str) -> List[str]:
    """
    Extract code snippets from text.
    
    Args:
        text: Text to extract code snippets from
        
    Returns:
        List of code snippets
    """
    # Extract code blocks with triple backticks (Markdown style)
    markdown_pattern = r"```(?:\w+)?\n(.*?)```"
    markdown_snippets = re.findall(markdown_pattern, text, re.DOTALL)
    
    # Extract code blocks with indentation (4+ spaces)
    indented_pattern = r"(?:^|\n)( {4,}[^\n]+(?:\n {4,}[^\n]+)*)"
    indented_snippets = re.findall(indented_pattern, text)
    indented_snippets = [snippet.strip() for snippet in indented_snippets]
    
    # Extract code blocks with HTML <code> or <pre> tags
    html_pattern = r"<(?:code|pre)>(.*?)</(?:code|pre)>"
    html_snippets = re.findall(html_pattern, text, re.DOTALL)
    
    # Combine all snippets
    all_snippets = markdown_snippets + indented_snippets + html_snippets
    
    # Filter out snippets that are too short or don't look like code
    filtered_snippets = []
    for snippet in all_snippets:
        snippet = snippet.strip()
        if len(snippet) > 10 and looks_like_code(snippet):
            filtered_snippets.append(snippet)
    
    return filtered_snippets

def looks_like_code(text: str) -> bool:
    """
    Check if text looks like code.
    
    Args:
        text: Text to check
        
    Returns:
        True if text looks like code, False otherwise
    """
    # Check for common code indicators
    code_indicators = [
        "=", "==", "===", "!=", "<", ">", "<=", ">=",  # Operators
        "if", "else", "for", "while", "def", "function", "class",  # Keywords
        "{", "}", "(", ")", "[", "]",  # Brackets
        ";", "import", "from", "return", "const", "var", "let",  # Other indicators
    ]
    
    # Count indicators
    indicator_count = sum(1 for indicator in code_indicators if indicator in text)
    
    # Check for indentation patterns
    lines = text.split("\n")
    indented_lines = sum(1 for line in lines if line.startswith("  ") or line.startswith("\t"))
    
    # Heuristic: if there are multiple indicators or consistent indentation, it's likely code
    return indicator_count >= 3 or (len(lines) > 3 and indented_lines / len(lines) > 0.5)

def process_code(snippet: str) -> Dict[str, Any]:
    """
    Process a code snippet to determine language and structure.
    
    Args:
        snippet: Code snippet to process
        
    Returns:
        Dictionary with processed code information
    """
    # Try to detect language
    language = detect_language(snippet)
    
    # Extract functions or classes
    functions = extract_functions(snippet, language)
    
    return {
        "language": language,
        "functions": functions,
        "snippet": snippet
    }

def detect_language(code: str) -> str:
    """
    Detect the programming language of a code snippet.
    
    Args:
        code: Code snippet
        
    Returns:
        Detected language name or "unknown"
    """
    try:
        lexer = lexers.guess_lexer(code)
        return lexer.name.lower()
    except ClassNotFound:
        # Try to guess based on keywords and syntax
        if "def " in code and ":" in code and ("self" in code or "import " in code):
            return "python"
        elif "function " in code and "{" in code and "}" in code:
            return "javascript"
        elif "public class " in code or "private void " in code:
            return "java"
        elif "#include <" in code and "int main" in code:
            return "c++"
        elif "<html" in code and "</html>" in code:
            return "html"
        elif "@" in code and ";" in code and "import " in code and "class " in code:
            return "java"
        else:
            return "unknown"

def extract_functions(code: str, language: str) -> List[str]:
    """
    Extract function or method names from code.
    
    Args:
        code: Code snippet
        language: Programming language
        
    Returns:
        List of function names
    """
    functions = []
    
    if language == "python":
        # Match Python function definitions
        pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        functions = re.findall(pattern, code)
    elif language in ["javascript", "typescript"]:
        # Match JavaScript/TypeScript function definitions
        pattern = r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        functions = re.findall(pattern, code)
        # Also match arrow functions and methods
        pattern2 = r"(?:const|let|var)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^)]*\)\s*=>"
        functions.extend(re.findall(pattern2, code))
    elif language in ["java", "c++", "c#"]:
        # Match Java/C++/C# method definitions
        pattern = r"(?:public|private|protected|static|\s)+[\w\<\>\[\]]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^\)]*\)\s*(?:\{|throws)"
        functions = re.findall(pattern, code)
    
    return functions