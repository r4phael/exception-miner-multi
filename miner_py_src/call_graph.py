import os
import subprocess
import json
import glob
from miner_py_src.exceptions import CallGraphError


def generate_cfg(project_name, project_folder):
    current_path = os.getcwd()
    os.makedirs(
        f'../output/call_graph/{project_name}', exist_ok=True)
    os.chdir(os.path.normpath(os.path.join(project_folder)))

    proc = subprocess.run([
        'pycg',
        *[os.path.abspath(x)
          for x in glob.iglob(f"./**/{project_name}/**/*.py", recursive=True)],
        *[os.path.abspath(x)
          for x in glob.iglob(f"./{project_name}.py", recursive=False)],
        '--package', project_name], stdout=subprocess.PIPE)

    if (proc.returncode != 0):
        raise CallGraphError(proc.stdout)

    os.chdir(current_path)

    json_obj = json.loads(proc.stdout)
    call_graph = {}
    for func_name, calls in json_obj.items():
        if func_name not in call_graph.keys():
            call_graph[func_name] = {
                'calls': [],
                'called_by': [],
            }

        for call in calls:
            call_graph[func_name]['calls'].append(call)

            if call not in call_graph.keys():
                call_graph[call] = {
                    'calls': [],
                    'called_by': [],
                }
            call_graph[call]['called_by'] = call_graph[call]['called_by'] or []
            call_graph[call]['called_by'].append(func_name)

    return call_graph


class CFG():
    def __init__(self, graph, catch_nodes):
        self.catch_nodes = catch_nodes
        self.graph = graph

    def get_uncaught_exceptions(self, func_name: str, raise_types: list[str]) -> dict[str, list[str]]:
        if (func_name not in self.graph.keys()):
            raise CallGraphError(f"CFG: {func_name} not found")

        export_data: dict[str, list[str]] = {}

        if len(self.graph[func_name]['called_by']) == 0:
            return export_data  # API call ??

        for called_by in self.graph[func_name]['called_by']:
            if called_by not in self.catch_nodes.keys():
                export_data[called_by] = raise_types
                continue

            for raise_type in raise_types:
                if raise_type not in self.catch_nodes[called_by]:
                    if called_by not in export_data.keys():
                        export_data[called_by] = []

                    export_data[called_by].append(raise_type)
                    export_data[called_by] = list(set(export_data[called_by]))

        return export_data
