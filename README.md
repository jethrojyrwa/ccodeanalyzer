# C Code Syntax Highlighter with Token Recognition

This project is a **C code syntax highlighter** built using **Streamlit** and **spaCy**. It tokenizes C code and highlights various components like keywords, identifiers, operators, constants, strings, punctuators, and preprocessor directives. The application provides an interactive interface to visualize syntax highlighting with real-time token recognition.

## Features

- **Syntax Highlighting**: Highlights C code components such as keywords, identifiers, constants, operators, strings, punctuators, and preprocessor directives.
- **Real-time Tokenization**: Displays token statistics for different categories such as **KEYWORDS**, **IDENTIFIERS**, **STRINGS**, **OPERATORS**, **PUNCTUATORS**, **CONSTANTS**, and **PREPROCESSORS**.
- **Dynamic Text Area**: The input text area dynamically adjusts its height according to the length of the entered code, making it more user-friendly.
- **Bar Chart for Token Distribution**: Visualize the distribution of tokens in the code through a bar chart.
- **Code Statistics**: Displays the total count of tokens categorized into different token types.

## Requirements

To run this project locally, you need to install the following dependencies:

- **Streamlit**: A Python library for building interactive web applications.
- **spaCy**: A Python library used for natural language processing.
- **Matplotlib**: A Python plotting library for visualizing token distribution.

To install the necessary dependencies, run the following command:

```bash
pip install streamlit spacy matplotlib
