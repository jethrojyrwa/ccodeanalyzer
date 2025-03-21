import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt


# sets which hold the different kind of tokens in c
KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
    "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict", "return",
    "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while", "_Alignas", "_Alignof", "_Atomic", "_Bool", "_Complex", "_Generic",
    "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local"
}

#operators
OPERATORS = {"+", "-", "*", "/", "%", "++", "--", "=", "+=", "-=", "*=", "/=", "%=", "==", "!=",
             ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"}

PUNCTUATORS = {";", ",", ".", ":", "(", ")", "{", "}", "[", "]"}

# color maps for defining the colour of each token in the NER
COLOR_MAP = {
    "KEYWORD": "#F92672",          # Pink (Red)
    "IDENTIFIER": "#FD971F",       # Red-Orange
    "STRING": "#A7E22E",           # Green
    "OPERATOR": "#66D9EF",         # Light Blue
    "PUNCTUATOR": "#AE81FF",       # Purple
    "CONSTANT": "#8B4513",         # Brown
    "PREPROCESSOR": "#888888"      # Gray for preprocessor directives
}

#handling removal of comments
def remove_comments(text):
    # '//.*' followed by any characters (.*) until the end of the line.
    text = re.sub(r'//.*', '', text) #sub searches for a given pattern and replaces it 

    #matches /* followed by any characters until */.    re.DOTALL allows the .*? to match across multiple lines.
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    return text

# function to tokenize and format code with syntax highlighting and token labels
def highlight_code(text):
    text = remove_comments(text)

    # split code into lines
    lines = text.split('\n') #splits when it encounters a new line
    
    highlighted_text = "" #holds output

    #for the dataframe
    token_stats = {
        "KEYWORD": 0,
        "IDENTIFIER": 0,
        "STRING": 0,
        "OPERATOR": 0,
        "PUNCTUATOR": 0,
        "CONSTANT": 0,
        "PREPROCESSOR": 0
    }
    
    # track the seen tokens to avoid duplicate token boxes for the same token
    seen_tokens = set()


    for line_number, line in enumerate(lines): #enumrate() returns the each line and the index of that line
        # process each line
        if line.strip() == "": #removes trailing and leading spaces 
            highlighted_text += "<br>"
            continue
            
        # handles preprocessor directives (e.g., #include, #define)
        if line.strip().startswith("#"): 
            directive = line.strip()
            highlighted_text += f'<span class="token-container"><span class="token-box preprocessor-token">{directive}</span><span class="token-type preprocessor-type">PREPROCESSOR</span></span><br>'
            token_stats["PREPROCESSOR"] += 1
            continue
        
        # process the line character by character to handle strings and other tokens
        i = 0
        line_output = ""
        indentation = len(line) - len(line.lstrip()) #calculates the number of spaces for indetatoin
        
        # Add indentation
        if indentation > 0:
            line_output += "&nbsp;" * indentation #to the particular line's output,a non-breaking space
        
        while i < len(line): #iteratres over the line
            # handles strings
            if line[i] == '"' or line[i] == "'": #checks if the character is a quotations
                quote_char = line[i] #stores either " or '
                start = i #keeps track of index at which string starts
                i += 1
                # finds the end of the string
                while i < len(line) and line[i] != quote_char:
                    if line[i] == '\\' and i + 1 < len(line): #checks to skip comments 
                        i += 2  #skips escaped characters
                    else:
                        i += 1
                
                if i < len(line):  # found the closing quote
                    i += 1  # includes the closing quote
                    string_content = line[start:i]
                    if string_content not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box string-token">{string_content}</span><span class="token-type string-type">STRING</span></span>'
                        seen_tokens.add(string_content)
                        token_stats["STRING"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box string-token" style="background-color:{COLOR_MAP["STRING"]}; color: white;">{string_content}</span></span>'
                else:
                    # in case of unclosed string case, it treats the rest of the line as a string which is unlikely to happen
                    string_content = line[start:]
                    if string_content not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box string-token">{string_content}</span><span class="token-type string-type">STRING</span></span>'
                        seen_tokens.add(string_content)
                        token_stats["STRING"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box string-token" style="background-color:{COLOR_MAP["STRING"]}; color: white;">{string_content}</span></span>'
                    i = len(line)
            
            # handles whitespace by adding to the index and moving on the the next
            elif line[i].isspace():
                line_output += line[i]
                i += 1
            
            # handles operators and punctuators
            elif any(line[i:i+len(op)] == op for op in sorted(OPERATORS | PUNCTUATORS, key=len, reverse=True)): #sorted combines OPERATORS and PUNCTUATORS into a single set. sorts the tokens by length in descending order (to match the longest token first).
                # find the longest matching operator or punctuator
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
                    # fallback - should not happen with well-formed code
                    line_output += line[i]
                    i += 1
            
            # handle identifiers, keywords, and constants
            else:
                # Find the token boundary
                start = i
                while i < len(line) and not line[i].isspace() and not any(line[i:i+len(op)] == op for op in sorted(OPERATORS | PUNCTUATORS, key=len, reverse=True)):
                    i += 1
                
                token = line[start:i]
                
                # identifies keywords
                if token in KEYWORDS:
                    if token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box keyword-token">{token}</span><span class="token-type keyword-type">KEYWORD</span></span>'
                        seen_tokens.add(token)
                        token_stats["KEYWORD"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box keyword-token" style="background-color:{COLOR_MAP["KEYWORD"]}; color: white;">{token}</span></span>'
                
                # identifies constants (numeric values, including hexadecimal and floating point numbers)
                elif token.isdigit() or (token.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in token[2:])) or re.match(r'^[0-9]*\.[0-9]+$', token):
                    if token not in seen_tokens:
                        line_output += f'<span class="token-container"><span class="token-box constant-token">{token}</span><span class="token-type constant-type">CONSTANT</span></span>'
                        seen_tokens.add(token)
                        token_stats["CONSTANT"] += 1
                    else:
                        line_output += f'<span class="token-container"><span class="token-box constant-token" style="background-color:{COLOR_MAP["CONSTANT"]}; color: white;">{token}</span></span>'
                
                # handles const-declared variables as constants (examples, const int x = 10;)
                elif line.strip().startswith("const") and len(line.strip().split()) > 2:
                    # Check for const declarations like 'const int varName = 10;'
                    parts = line.strip().split() #splits the line further into parts for processing
                    if parts[0] == "const" and parts[1] in KEYWORDS:  # e.g., const int
                        if token not in seen_tokens:
                            line_output += f'<span class="token-container"><span class="token-box constant-token">{token}</span><span class="token-type constant-type">CONSTANT</span></span>'
                            seen_tokens.add(token)
                            token_stats["CONSTANT"] += 1
                        else:
                            line_output += f'<span class="token-container"><span class="token-box constant-token" style="background-color:{COLOR_MAP["CONSTANT"]}; color: white;">{token}</span></span>'
                
                # identifiers are handled here
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

# Legend which indicates which colour is for which kind of token
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
    # adds a file uploader for C code 
    uploaded_file = st.file_uploader("Upload a C program file", type=["c", "txt"])

    if uploaded_file is not None:
    #reads the uploaded file
        code_input = uploaded_file.read().decode("utf-8")
    else:
        # default to text area for manual input if uploaded file is not available
        code_input = st.text_area("Enter your C code:", height=300, value="""#include <stdio.h>

const int MAX = 100;
const float PI = 3.14;
char name[] = "John";

if (MAX > 50) {
    printf("%s\\n", name);
}

return 0;""")


        st.button("Tokenize and Highlight", key="highlight_button") #tokenises the program

with col2:
    # checks if code has been provided
    if code_input:
        highlighted_code, token_stats = highlight_code(code_input)

        # displays highlighted code using markdown with HTML rendering
        st.markdown(TOKEN_STYLE_CSS + f'<pre>{highlighted_code}</pre>', unsafe_allow_html=True)

        # display token statistics in a horizontal layout
        st.markdown("### Token Statistics")
        stats_df = pd.DataFrame(list(token_stats.items()), columns=["Token Type", "Count"]) #creates a dataframe from the token stats which we have kept track of
        
        # displays a bar chart for token distribution
        st.markdown("### Token Distribution")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(stats_df["Token Type"], stats_df["Count"], color=[COLOR_MAP[t] for t in stats_df["Token Type"]])
        ax.set_xlabel("Token Type")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # displays a token counts in a table
        st.table(stats_df)