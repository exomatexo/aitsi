import argparse
import json
import logging
import logging.config as conf
import os
import time
from typing import Dict

from pandas import DataFrame

from aitsi_parser.CsvBuilder import CsvBuilder
from aitsi_parser.Parser import Parser

log = logging.getLogger(__name__)


def export_AST_to_file(json_ast: Dict[str, dict], filename: str = "AST.json") -> None:
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=4, sort_keys=True)


def read_program_from_file(filename: str = "code_short.txt") -> Parser:
    with open(filename) as g:
        _parser: Parser = Parser(g.read(), filename)
        return _parser


def main(simple_file_path: str = "code_short.txt", tree_output: str = "AST.json",
         output_directory: str = "test") -> str:
    current = time.time()
    parser: Parser = read_program_from_file(simple_file_path)
    parser.program()
    # json_tree: Dict[str, dict] = parser.get_node_json()
    # result = [parser.next_table.get_next(n) for n in range(1,312)]
    ##todo można odkomentować żeby wypisac sobie dane cyk najlepiej zmienic na logi
    # log.debug(json_tree)
    # log.debug(parser.var_table.to_log())
    # log.debug(parser.proc_table.to_log())
    # log.debug(parser.calls_table.to_log())
    # log.debug(parser.mod_table.to_log())
    # log.debug(parser.parent_table.to_log())
    # log.debug(parser.uses_table.to_log())
    # log.debug(parser.follows_table.to_log())
    # log.debug(parser.statement_table.to_log())
    # log.debug(parser.const_table.to_log())
    # log.debug(parser.next_table.to_log())
    dirname, filename = os.path.split(os.path.abspath(__file__))
    path: str = os.path.join(dirname, "database/", output_directory, os.path.basename(simple_file_path).split('.')[0],
                             "")
    os.makedirs(path, exist_ok=True)
    export_AST_to_file(parser.get_node_json(), path + tree_output)
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.var_table), path + "VarTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.proc_table), path + "ProcTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.statement_table), path + "StatementTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame([{'constant': key, 'other_info':{'lines': parser.const_table[key]['lines']}} for key in parser.const_table]), path + "ConstTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.follows_table).transpose(), path + "FollowsTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.parent_table).transpose(), path + "ParentTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.calls_table).transpose(), path + "CallsTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.next_table), path + "NextTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.mod_table), path + "ModifiesTable.csv")
    CsvBuilder.save_table_to_csv_file(DataFrame(parser.uses_table), path + "UsesTable.csv")
    # todo - dodać resztę tabelek jak będą :*
    # print(time.time() - current)
    return path


if __name__ == '__main__':
    conf.fileConfig("logging.conf", disable_existing_loggers=False)
    arg_parser = argparse.ArgumentParser(description='Aitsi parser!')
    arg_parser.add_argument("--i", default="code_short.txt", type=str, help="Input file with program")
    arg_parser.add_argument("--o", default="AST.json", type=str, help="Output file for AST json ")
    arg_parser.add_argument("--d", default="test", type=str, help="Name of output directory")
    args: argparse.Namespace = arg_parser.parse_args()
    input_filename: str = args.i
    tree_filename: str = args.o
    output_filename: str = args.d
    main(input_filename, tree_filename, output_filename)
