import os
import subprocess
import json
from miner_py_src.exceptions import CallGraphError

"""
`Install graphviz cpan:`

sudo apt install build-essential
sudo apt install libexpat1-dev
sudo apt install graphviz
sudo cpan install GraphViz

`Install JSON modules:`

sudo cpan install JSON::XS

`Install callGraph:`

sudo apt install unzip
wget -o- https://github.com/koknat/callGraph/archive/refs/heads/main.zip
unzip -a main.zip
rm main.zip
mv callGraph-main/ callGraph
cd callGraph/
sudo ln -s /home/<username>/callGraph/callGraph /usr/bin/callGraph
sudo chmod ugo+x /usr/bin/callGraph
"""


def generate_cfg(project_name, project_folder):
    current_path = os.getcwd()
    os.makedirs(
        f'../output/call_graph/{project_name}', exist_ok=True)
    os.chdir(os.path.normpath(os.path.join(project_folder, '../')))

    jsnout = os.path.normpath(os.path.join(
        current_path, f"../output/call_graph/{project_name}/saida.json"))
    output = os.path.normpath(os.path.join(
        current_path, f"../output/call_graph/{project_name}/saida.dot"))

    subprocess.run(
        [
            "callGraph", project_name,
            "--jsnOut", jsnout,
            "--output", output,
            "--language", "py"
        ]
    )
    os.chdir(current_path)

    json_file = open(jsnout, "r")
    json_obj = json.load(json_file)
    return json_obj


class CFG():
    def __init__(self, graph, catch_nodes):
        self.catch_nodes = catch_nodes
        self.graph = graph

    def get_uncaught_exceptions(self, func_name: str, raise_types: list[str]) -> dict[str, str]:
        if (func_name not in self.graph.keys()):
            raise CallGraphError(f"CFG: {func_name} not found")

        export_data = {}

        if 'called_by' not in self.graph[func_name].keys():
            return export_data  # API call ??

        for called_by in self.graph[func_name]['called_by'].keys():
            if called_by not in self.catch_nodes.keys():
                continue

            for raise_type in raise_types:
                if raise_type not in self.catch_nodes[called_by]:
                    if called_by not in export_data.keys():
                        export_data[called_by] = []

                    export_data[called_by].append(raise_type)
                    export_data[called_by] = list(set(export_data[called_by]))

        return export_data
