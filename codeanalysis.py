import streamlit as st
import spacy
import re
import pandas as pd
import matplotlib.pyplot as plt

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define C language components
KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
    "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict", "return",
    "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while", "_Alignas", "_Alignof", "_Atomic", "_Bool", "_Complex", "_Generic",
    "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local"
}

OPERATORS = {"+", "-", "*", "/", "%", "++", "--", "=", "+=", "-=", "*=", "/=", "%=", "==", "!=",
             ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"}

PUNCTUATORS = {";", ",", ".", ":", "(", ")", "{", "}", "[", "]"}

# Define color mapping for different token types
COLOR_MAP = {
    "KEYWORD": "#F92672",          # Pink (Red)
    "IDENTIFIER": "#FD971F",       # Red-Orange
    "STRING": "#A7E22E",           # Green
    "OPERATOR": "#66D9EF",         # Light Blue
    "PUNCTUATOR": "#AE81FF",       # Purple
    "CONSTANT": "#8B4513",         # Brown
    "PREPROCESSOR": "#888888"      # Gray for preprocessor directives
}

def remove_comments(text):
    # Remove single-line comments (//)
    text = re.sub(r'//.*', '', text)
    
    # Remove multi-line comments (/* ... */), including multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    return text

# Function to tokenize and format code with syntax highlighting and token labels
def highlight_code(text):
    text = remove_comments(text)
    # Split code into lines
    lines = text.split('\n')
    
    highlighted_text = ""
    token_stats = {
        "KEYWORD": 0,
        "IDENTIFIER": 0,
        "STRING": 0,
        "OPERATOR": 0,
        "PUNCTUATOR": 0,
        "CONSTANT": 0,
        "PREPROCESSOR": 0
    }
    
    # Track seen tokens to avoid duplicate token boxes
    seen_tokens = set()

    for line_number, line in enumerate(lines):
        # Process each line
        if line.strip() == "":
            highlighted_text += "<br>"
            continue
            
        # Handle preprocessor directives (e.g., #include)
        if line.strip().startswith("#"):
            directive = line.strip()
            highlighted_text += f'<span class="token-container"><span class="token-box preprocessor-token">{directive}</span><span class="token-type preprocessor-type">PREPROCESSOR</span></span><br>'
            token_stats["PREPROCESSOR"] += 1
            continue
        
        # Process the line character by character to handle strings and other tokens
        i = 0
        line_output = ""
        indentation = len(line) - len(line.lstrip())
        
        # Add indentation
        if indentation > 0:
            line_output += "&nbsp;" * indentation
        
        while i < len(line):
            # Handle strings
            if line[i] == '"' or line[i] == "'":
                quote_char = line[i]
                start = i
                i += 1
                # Find the end of the string
                while i < len(line) and line[i] != quote_char:
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # Skip escaped characters
                    else:
                        i += 1
                
                if i < len(line):  # Found closing quote
                    i += 1  # Include the closing quote
                    string_content = line[start:i]
                    if string_content not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box string-token">{string_content}</span><span class="token-type string-type">STRING</span></span>'
                        seen_tokens.add(string_content)
                        token_stats["STRING"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box string-token" style="background-color:{COLOR_MAP["STRING"]}; color: white;">{string_content}</span></span>'
                else:
                    # Unclosed string, treat the rest as a string
                    string_content = line[start:]
                    if string_content not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box string-token">{string_content}</span><span class="token-type string-type">STRING</span></span>'
                        seen_tokens.add(string_content)
                        token_stats["STRING"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box string-token" style="background-color:{COLOR_MAP["STRING"]}; color: white;">{string_content}</span></span>'
                    i = len(line)
            
            # Handle whitespace
            elif line[i].isspace():
                line_output += line[i]
                i += 1
            
            # Handle operators and punctuators
            elif any(line[i:i+len(op)] == op for op in sorted(OPERATORS | PUNCTUATORS, key=len, reverse=True)):
                # Find the longest matching operator or punctuator
                matched_token = None
                for token in sorted(OPERATORS | PUNCTUATORS, key=len, reverse=True):
                    if i + len(token) <= len(line) and line[i:i+len(token)] == token:
                        matched_token = token
                        break
                
                if matched_token:
                    token_type = "OPERATOR" if matched_token in OPERATORS else "PUNCTUATOR"
                    token_type_lower = token_type.lower()
                    if matched_token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box {token_type_lower}-token">{matched_token}</span><span class="token-type {token_type_lower}-type">{token_type}</span></span>'
                        seen_tokens.add(matched_token)
                        token_stats[token_type] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box {token_type_lower}-token" style="background-color:{COLOR_MAP[token_type]}">{matched_token}</span></span>'
                    i += len(matched_token)
                else:
                    # Fallback - should not happen with well-formed code
                    line_output += line[i]
                    i += 1
            
            # Handle identifiers, keywords, and constants
            else:
                # Find the token boundary
                start = i
                while i < len(line) and not line[i].isspace() and not any(line[i:i+len(op)] == op for op in sorted(OPERATORS | PUNCTUATORS, key=len, reverse=True)):
                    i += 1
                
                token = line[start:i]
                
                # Identify keywords
                if token in KEYWORDS:
                    if token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box keyword-token">{token}</span><span class="token-type keyword-type">KEYWORD</span></span>'
                        seen_tokens.add(token)
                        token_stats["KEYWORD"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box keyword-token" style="background-color:{COLOR_MAP["KEYWORD"]}; color: white;">{token}</span></span>'
                
                # Identify constants (numeric values, including hexadecimal and floating point numbers)
                elif token.isdigit() or (token.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in token[2:])) or re.match(r'^[0-9]*\.[0-9]+$', token):
                    if token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box constant-token">{token}</span><span class="token-type constant-type">CONSTANT</span></span>'
                        seen_tokens.add(token)
                        token_stats["CONSTANT"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box constant-token" style="background-color:{COLOR_MAP["CONSTANT"]}; color: white;">{token}</span></span>'
                
                # Handle const-declared variables as constants (e.g., const int x = 10;)
                elif line.strip().startswith("const") and len(line.strip().split()) > 2:
                    # Check for const declarations like 'const int varName = 10;'
                    parts = line.strip().split()
                    if parts[0] == "const" and parts[1] in KEYWORDS:  # e.g., const int
                        if token not in seen_tokens:
                            line_output += f'<span class="token-container"><span class="token-box constant-token">{token}</span><span class="token-type constant-type">CONSTANT</span></span>'
                            seen_tokens.add(token)
                            token_stats["CONSTANT"] += 1
                        else:
                            line_output += f'<span class="token-container"><span class="token-box constant-token" style="background-color:{COLOR_MAP["CONSTANT"]}; color: white;">{token}</span></span>'
                
                # Identifiers (including digits treated as identifiers)
                elif token.isidentifier():
                    if token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box identifier-token">{token}</span><span class="token-type identifier-type">IDENTIFIER</span></span>'
                        seen_tokens.add(token)
                        token_stats["IDENTIFIER"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box identifier-token" style="background-color:{COLOR_MAP["IDENTIFIER"]}; color: white;">{token}</span></span>'
        
        highlighted_text += line_output + "<br>"
    
    return highlighted_text, token_stats


# CSS for the token boxes
# CSS for the token boxes
TOKEN_STYLE_CSS = """
<style>
.token-container {
    display: inline-flex;
    margin: 2px;
    vertical-align: middle;
}

.token-box {
    display: inline-block;
    font-family: 'Courier New', monospace;  /* Set to Courier New */
    padding: 2px 6px;
    border-radius: 3px 0 0 3px;
    color: white;
    font-weight: bold;
}

.token-type {
    display: inline-block;
    font-size: 10px;
    font-family: 'Courier New', monospace;  /* Set to Courier New */
    padding: 2px 4px;
    border-radius: 0 3px 3px 0;
    background-color: #444;
    color: white;
    font-weight: bold;
}

.keyword-token {
    background-color: #F92672;
}

.identifier-token {
    background-color: #FD971F;
}

.string-token {
    background-color: #A7E22E;
}

.operator-token {
    background-color: #66D9EF;
}

.punctuator-token {
    background-color: #AE81FF;
}

.constant-token {
    background-color: #8B4513;
}

.preprocessor-token {
    background-color: #888888;
}

.keyword-type, .identifier-type, .string-type, .operator-type, 
.punctuator-type, .constant-type, .preprocessor-type {
    background-color: #444;
}

pre {
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 5px;
    font-family: 'Courier New', monospace;  /* Set to Courier New */
    line-height: 1.8;
    border: 1px solid #ddd;
}
</style>
"""

# Streamlit UI
st.set_page_config(page_title="C Code Syntax Highlighter", layout="wide")
st.title("C Code Syntax Highlighter with Token Recognition")

# Legend
st.markdown("### Legend")
legend_html = """
<div style="display: flex; flex-wrap: wrap;">
    <div style="margin-right: 20px;"><span style="color: #F92672;"><b>● Keyword</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #FD971F;"><b>● Identifier</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #A7E22E;"><b>● String</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #66D9EF;"><b>● Operator</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #AE81FF;"><b>● Punctuator</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #8B4513;"><b>● Constant</b></span></div>
    <div style="margin-right: 20px;"><span style="color: #888888;"><b>● Preprocessor</b></span></div>
</div>
"""
st.markdown(legend_html, unsafe_allow_html=True)

# Text area for input
col1, col2 = st.columns([2, 3])

with col1:
    code_input = st.text_area("Enter your C code:", height=300, value="""#include <stdio.h>

const int MAX = 100;
const float PI = 3.14;
char name[] = "John";

if (MAX > 50) {
    printf("%s\\n", name);
}

return 0;""")

    st.button("Tokenize and Highlight", key="highlight_button")

with col2:
    # Check if code has been provided
    if code_input:
        highlighted_code, token_stats = highlight_code(code_input)

        # Display highlighted code using markdown with HTML rendering
        st.markdown(TOKEN_STYLE_CSS + f'<pre>{highlighted_code}</pre>', unsafe_allow_html=True)

        # Display token statistics in a horizontal layout
        st.markdown("### Token Statistics")
        stats_df = pd.DataFrame(list(token_stats.items()), columns=["Token Type", "Count"])
        
        # Display bar chart for token distribution
        st.markdown("### Token Distribution")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(stats_df["Token Type"], stats_df["Count"], color=[COLOR_MAP[t] for t in stats_df["Token Type"]])
        ax.set_xlabel("Token Type")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Display token counts in a table
        st.table(stats_df)