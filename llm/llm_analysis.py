import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import ast
import re
from difflib import SequenceMatcher

# Load the dataset
df = pd.read_csv("/home/r4ph/desenv/exception-miner-multi/llm/data/new_flask_llm_results.csv")

def extract_statements(code):
    try:
        tree = ast.parse(code)
        return [node for node in ast.walk(tree) if isinstance(node, ast.stmt)]
    except:
        return []

""" Function to create vector representation of try block. 
For example, if the code has 3 statements inside the try block that contains 6 statements, the vector will be [1, 1, 1, 0, 0, 0]
"""
def create_try_vector(code):
    statements = extract_statements(code)
    vector = [0] * len(statements)
    
    for i, stmt in enumerate(statements):
        if isinstance(stmt, ast.Try):
            for body_stmt in stmt.body:
                start = body_stmt.lineno
                end = body_stmt.end_lineno
                vector[start-1:end] = [1] * (end - start + 1)
    
    return vector

# Function to parse LLM response for task2
def parse_task_response2(response):
    try:
        code_block = re.search(r'except.*?:(.*?)(?=\n\S|\Z)', response, re.DOTALL).group(0)
        return f"try:\n    pass\n{code_block}"
    except:
        return "try:\n    pass\nexcept Exception:\n    pass"

# Function to parse LLM response for task3
def parse_task3_response(response):
    # Split the response by commas and strip whitespace
    exceptions = [exc.strip() for exc in response.split(',')]
    # Remove any empty strings
    exceptions = [exc for exc in exceptions if exc]
    return exceptions

# Function to parse str_except_identifiers
def parse_str_except_identifiers(identifiers):
    try:
        # Convert string representation of list to actual list
        return ast.literal_eval(identifiers)
    except:
        return []

# Function to extract except block from LLM response for task4
def extract_except_block(response):
    try:
        # Extract code block from the response
        code_block = re.search(r'```python\n(.*?)```', response, re.DOTALL).group(1)
        return code_block.strip()
    except:
        return ""

# Function to calculate similarity between two code blocks
def code_similarity(code1, code2):
    return SequenceMatcher(None, code1, code2).ratio()

# Define the tasks
tasks = ['task1', 'task2', 'task3', 'task4']

# Evaluate metrics for each task
for task in tasks:
    print(f"\nEvaluating {task}:")
    
    df_task = df[df['task'] == task]
    
    for prompt_type in df_task['prompt_type'].unique():
        results = df_task[df_task['prompt_type'] == prompt_type]
        
        if task == 'task1':
            y_true = results['n_try_except']
            y_pred = results['llm_response'].apply(lambda x: 1 if 'yes' in x.lower() else 0)
        elif task == 'task3':
            y_true = results['str_except_identifiers'].apply(parse_str_except_identifiers)
            y_pred = results['llm_response'].apply(parse_task3_response)
            
            # Calculate accuracy for task3
            accuracy = sum(set(true) == set(pred) for true, pred in zip(y_true, y_pred)) / len(y_true)
            
            # Calculate precision, recall, and F1-score for task3
            true_flat = [item for sublist in y_true for item in sublist]
            pred_flat = [item for sublist in y_pred for item in sublist]
            
            precision = precision_score(true_flat, pred_flat, average='micro', zero_division=0)
            recall = recall_score(true_flat, pred_flat, average='micro', zero_division=0)
            f_measure = f1_score(true_flat, pred_flat, average='micro', zero_division=0)
            
            print(f"\nMetrics for {prompt_type} prompt:")
            print(f"Accuracy: {accuracy:.2f}")
            print(f"Precision: {precision:.2f}")
            print(f"Recall: {recall:.2f}")
            print(f"F-measure: {f_measure:.2f}")
            
            continue
        elif task == 'task4':
            y_true = results['str_except_block']
            y_pred = results['llm_response'].apply(extract_except_block)
            
            # Calculate similarity scores
            similarities = [code_similarity(true, pred) for true, pred in zip(y_true, y_pred)]
            
            # Calculate metrics
            accuracy = np.mean(similarities)
            
            print(f"\nMetrics for {prompt_type} prompt:")
            print(f"Average Similarity: {accuracy:.2f}")
            
            # Plot histogram of similarity scores
            plt.figure(figsize=(8, 6))
            plt.hist(similarities, bins=20, edgecolor='black')
            plt.title(f"Similarity Scores Distribution for {task} - {prompt_type}")
            plt.xlabel("Similarity Score")
            plt.ylabel("Frequency")
            plt.show()
            
            continue
        else:  # task2
            y_true = []
            y_pred = []
            for _, row in results.iterrows():
                original_vector = create_try_vector(row['func_body'])
                llm_vector = create_try_vector(parse_task_response2(row['llm_response']))
                
                max_len = max(len(original_vector), len(llm_vector))
                original_vector += [0] * (max_len - len(original_vector))
                llm_vector += [0] * (max_len - len(llm_vector))
                
                y_true.extend(original_vector)
                y_pred.extend(llm_vector)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f_measure = f1_score(y_true, y_pred, zero_division=0)
        
        print(f"\nMetrics for {prompt_type} prompt:")
        print(f"Accuracy: {accuracy:.2f}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F-measure: {f_measure:.2f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        print("\nConfusion Matrix:")
        print(cm)
        
        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Predicted No', 'Predicted Yes'],
                    yticklabels=['Actual No', 'Actual Yes'])
        plt.title(f"Confusion Matrix for {task} - {prompt_type}")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.show()

