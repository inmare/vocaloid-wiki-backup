from database.create_db import (
    create_db_and_tables,
    create_title,
    create_page,
)
import os
import shutil


def create_json_dir(delete_old_folder=False):
    if delete_old_folder:
        if os.path.exists("json/data"):
            shutil.rmtree("json/data")
    os.makedirs("json/data")


# import json

# json_list = os.listdir("json/temp")
# data_list = []
# for json_file in json_list:
#     with open(f"json/temp/{json_file}", "r", encoding="utf-8") as f:
#         data = json.load(f)
#         data_list.append(data)

create_json_dir(delete_old_folder=True)
create_db_and_tables(delete_old_db=True)
create_title()

# for data in data_list:
#     create_page(data)

# 노래 검색
# page = find_page("/telecaster-b-boy")
