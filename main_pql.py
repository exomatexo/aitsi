import argparse
import json
from typing import Dict, Union

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ConstTable import ConstTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.NextTable import NextTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.QueryEvaluator import QueryEvaluator
from pql.QueryProcessor import QueryProcessor
from pql.utils.JsonReader import JsonReader


def load_ast_from_file(filename: str) -> Node:
    with open(filename) as g:
        loaded_node: Node = Node.Schema().loads(g.read())
        return loaded_node


def load_query_from_file(filename: str) -> str:
    with open(filename) as g:
        _query: str = g.read()
        return _query


def export_query_tree_to_file(query_json_tree: Dict[str, dict], filename: str = "pql_query_tree.json") -> None:
    with open(filename, 'w') as f:
        json.dump(query_json_tree, f, indent=4, sort_keys=True)


class PQL:
    def __init__(self, tables_directory_path: str = "database/test/code_short", input_ast_filename: str = "AST.json"):
        self.ast_node: Node = load_ast_from_file(tables_directory_path + "/" + input_ast_filename)
        var_table: VarTable = VarTable(JsonReader.read_json_from_file(tables_directory_path + "/VarTable.json"))
        proc_table: ProcTable = ProcTable(JsonReader.read_json_from_file(tables_directory_path + "/ProcTable.json"))
        calls_table: CallsTable = CallsTable(
            JsonReader.read_json_from_file(tables_directory_path + "/CallsTable.json"))
        modifies_table: ModifiesTable = ModifiesTable(
            JsonReader.read_json_from_file(tables_directory_path + "/ModifiesTable.json"))
        parent_table: ParentTable = ParentTable(
            JsonReader.read_json_from_file(tables_directory_path + "/ParentTable.json"))
        uses_table: UsesTable = UsesTable(JsonReader.read_json_from_file(tables_directory_path + "/UsesTable.json"))
        follows_table: FollowsTable = FollowsTable(
            JsonReader.read_json_from_file(tables_directory_path + "/FollowsTable.json"))
        statement_table: StatementTable = StatementTable(
            JsonReader.read_json_from_file(tables_directory_path + "/StatementTable.json"))
        const_table: ConstTable = ConstTable(
            JsonReader.read_json_from_file(tables_directory_path + "/ConstTable.json"))
        next_table: NextTable = NextTable(
            JsonReader.read_json_from_file(tables_directory_path + "/NextTable.json"))
        self.all_tables: Dict[str, Union[VarTable,
                                         ProcTable,
                                         UsesTable,
                                         ParentTable,
                                         ModifiesTable,
                                         FollowsTable,
                                         CallsTable,
                                         StatementTable,
                                         ConstTable,
                                         NextTable]] = {'var': var_table,
                                                        'proc': proc_table,
                                                        'uses': uses_table,
                                                        'parent': parent_table,
                                                        'modifies': modifies_table,
                                                        'follows': follows_table,
                                                        'calls': calls_table,
                                                        'statement': statement_table,
                                                        'const': const_table,
                                                        'next': next_table}

    def main(self, query: str, output_query_filename: str = "pql_query_tree.json", save_to_file: bool = False) -> str:
        query_processor: QueryProcessor = QueryProcessor(self.all_tables['proc'].get_all_proc_name(),
                                                         self.all_tables['var'].get_all_var_name(),
                                                         self.all_tables['statement'].get_size())
        try:
            query_processor.generate_query_tree(query)
        except Exception as e:
            return str(e)
        query_tree: Dict[str, dict] = query_processor.get_node_json()
        query_evaluator: QueryEvaluator = QueryEvaluator(self.all_tables, self.ast_node)
        try:
            response = query_evaluator.evaluate_query(query_processor.root)
        except Exception as e:
            if query_evaluator.results_table.select[0] == 'BOOLEAN':
                return 'false'
            else:
                return 'none'
        if save_to_file:
            export_query_tree_to_file(query_tree, output_query_filename)
        return response


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='PQL program!')
    arg_parser.add_argument("--i", default="pql_query.txt", type=str, help="Input file with pql query")
    arg_parser.add_argument("--o", default="pql_query_tree.json", type=str, help="Output file for pql query tree ")
    arg_parser.add_argument("--ast", default="AST.json", type=str, help="Input file with AST tree")
    arg_parser.add_argument("--p", default="database/test/code_short", type=str, help="Path to dir")

    args: argparse.Namespace = arg_parser.parse_args()
    _input_query_filename: str = args.i
    _input_ast_filename: str = args.ast
    _output_query_filename: str = args.o
    _tables_directory_path: str = args.p
    _query: str = load_query_from_file(_input_query_filename)
    pql = PQL(_tables_directory_path)
    result: str = pql.main(_query)
