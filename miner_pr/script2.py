import os
import json
import requests
import subprocess
import csv
from pydriller import Repository
from pydriller.domain.commit import ModificationType
import ast
import re

def commit_exists(repo_path, commit_hash):
    try:
        subprocess.check_output(['git', '-C', repo_path, 'rev-parse', '--verify', commit_hash], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def get_merged_prs(repo, token):
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {token}"}
    params = {"state": "closed", "per_page": 100}
    prs = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        prs.extend([pr for pr in data if pr['merged_at']])
        url = response.links.get('next', {}).get('url')

    return prs

def get_pr_commits(repo, pr_number, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def mine_commits(repo_path, commit_hashes):
    commits_data = []
    for commit_hash in commit_hashes:
        if not commit_exists(repo_path, commit_hash):
            continue
        
        try:
            for commit in Repository(repo_path, single=commit_hash).traverse_commits():
                commit_info = {
                    'hash': commit.hash,
                    'msg': commit.msg,
                    'modifications': []
                }
                for mod in commit.modified_files:
                    if mod.change_type == ModificationType.MODIFY:
                        commit_info['modifications'].append({
                            'filename': mod.filename,
                            'diff': mod.diff,
                            'source_code_before': mod.source_code_before,
                            'source_code': mod.source_code
                        })
                commits_data.append(commit_info)
        except Exception as e:
            print(f"Error processing commit {commit_hash}: {e}")
    return commits_data

def save_prs_to_file(prs, filename):
    with open(filename, 'w') as file:
        json.dump(prs, file, indent=4)

def load_prs_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def parse_functions(source_code):
    try:
        cleaned_source_code = source_code.replace('\x00', '')
        tree = ast.parse(cleaned_source_code)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'body': ast.unparse(node),
                    'start_lineno': node.lineno,
                    'end_lineno': node.end_lineno,
                    'has_docstring': ast.get_docstring(node) is not None
                })
        return functions
    except SyntaxError:
        return []

def match_functions(before_funcs, after_funcs):
    matched_funcs = []
    for before in before_funcs:
        for after in after_funcs:
            if before['name'] == after['name']:
                matched_funcs.append((before, after))
                break
    return matched_funcs

def has_try_except(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Try):
            return True
    return False

def has_docstring(node):
    return ast.get_docstring(node) is not None

def get_function_body(node):
    return ast.unparse(node)

def find_associated_tests_in_pr(modifications, modified_filename):
    test_files = []
    base_name = os.path.basename(modified_filename)
    test_indicators = ['test_', '_test', 'tests']
    test_pattern = re.compile(r'^[A-Za-z]+_[A-Za-z]+_[A-Za-z]+$')

    for mod in modifications:
        if any(indicator in mod['filename'] for indicator in test_indicators) or test_pattern.match(os.path.basename(mod['filename'])):
            if base_name.split('.')[0] in mod['filename']:
                test_files.append(mod['filename'])
    return test_files

def analyze_commits(commits_data):
    results = []
    for pr_number, commits in commits_data.items():
        for commit in commits:
            for mod in commit['modifications']:
                before_funcs = parse_functions(mod['source_code_before'])
                after_funcs = parse_functions(mod['source_code'])
                matched_funcs = match_functions(before_funcs, after_funcs)
                for before, after in matched_funcs:
                    if not has_try_except(ast.parse(before['body'])) and has_try_except(ast.parse(after['body'])):
                        associated_tests = find_associated_tests_in_pr(commit['modifications'], mod['filename'])
                        results.append({
                            'pr_number': pr_number,
                            'commit_hash': commit['hash'],
                            'filename': mod['filename'],
                            'function_name': after['name'],
                            'has_docstring': after['has_docstring'],
                            'before_body': before['body'],
                            'after_body': after['body'],
                            'has_associated_test': bool(associated_tests),
                            'associated_tests': associated_tests
                        })
    return results

def save_results_to_csv(results, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'pr_number', 'commit_hash', 'filename', 'function_name', 
            'has_docstring', 'before_body', 'after_body', 
            'has_associated_test', 'associated_tests'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    repo = "pallets/flask"
    token = "your_github_token"
    repo_path = "/home/tales/Documents/code/flask"

    os.system(f"git -C {repo_path} fetch --unshallow")

    prs_file = "/home/tales/Documents/code/exception-miner-multi/miner_pr/merged_prs.json"
    if os.path.exists(prs_file):
        merged_prs = load_prs_from_file(prs_file)
    else:
        merged_prs = get_merged_prs(repo, token)
        save_prs_to_file(merged_prs, prs_file)
    
    commits_file = "/home/tales/Documents/code/exception-miner-multi/miner_pr/all_commits.json"
    if os.path.exists(commits_file):
        all_commits = load_prs_from_file(commits_file)
    else:
        all_commits = {}
        for pr in merged_prs:
            pr_number = pr['number']
            commits = get_pr_commits(repo, pr_number, token)
            all_commits[pr_number] = [commit['sha'] for commit in commits]
        save_prs_to_file(all_commits, commits_file)
    
    commits_data = {}
    for pr_number, commit_hashes in all_commits.items():
        commits_data[pr_number] = mine_commits(repo_path, commit_hashes)
    save_prs_to_file(commits_data, "/home/tales/Documents/code/exception-miner-multi/miner_pr/commits_data.json")

    results = analyze_commits(commits_data)
    save_results_to_csv(results, "/home/tales/Documents/code/exception-miner-multi/miner_pr/exception_mechanisms.csv")