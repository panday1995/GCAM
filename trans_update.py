import os
import xml.etree.ElementTree as et

import numpy as np
import pandas as pd

# UCD_trn xml file path
extra_xml_path = r"D:\tencent_files\chrome_Download\Research\Equilibium_modelling\Partial_equilibium\GCAM\gcam-v7.1\input\extra"
dir_extra = os.listdir(extra_xml_path)  # SSP3 uses trn_UCD_SSP3
trn_xml_ls = [
    file
    for file in dir_extra
    if "transportation_UCD_SSP" in file and "_new" not in file
]
trn_xml_path = dict(
    zip(
        ["ssp" + str(i) for i in [1, 2, 4, 5]],
        [os.path.join(extra_xml_path, file) for file in trn_xml_ls],
    )
)

node_tag_ls = ["minicam-non-energy-input", "minicam-energy-input", "loadFactor"]
subnode_tag_ls = ["input-cost", "coefficient"]
supplysector_name_ls = ["trn_pass_road_LDV_4W", "trn_freight_road"]


def xml_input_revise(
    path,
    new_file_name,
    data_input,
    supplysector_name_ls=supplysector_name_ls,
    node_tag_ls=node_tag_ls,
    subnode_tag_ls=subnode_tag_ls,
):
    data = data_input
    xtree = et.parse(path)
    xroot = xtree.getroot()
    rows = []
    for child in xroot:
        for region in child:
            if region.attrib.get("name") == "China":
                for supplysector in region:
                    if (
                        supplysector.attrib.get("name") in supplysector_name_ls
                    ):  # supplysector_name
                        for tranSubsector in supplysector:
                            if tranSubsector.attrib.get("name") in data.index.unique(
                                level="tranSubsector"
                            ):
                                for stubtechnology in tranSubsector:
                                    if stubtechnology.attrib.get(
                                        "name"
                                    ) in data.index.unique("stubtechnology"):
                                        for period in stubtechnology:
                                            if period.attrib.get("year") in [
                                                str(y) for y in data.columns
                                            ]:  # period_to_rev:
                                                for node in period:
                                                    if node.tag in node_tag_ls:
                                                        try:
                                                            tranSubsector_name = tranSubsector.attrib.get(
                                                                "name"
                                                            )
                                                            stubtechnology_name = stubtechnology.attrib.get(
                                                                "name"
                                                            )
                                                            year = int(
                                                                period.attrib.get(
                                                                    "year"
                                                                )
                                                            )
                                                            if node.tag == "loadFactor":
                                                                node.text = str(
                                                                    data.loc[
                                                                        (
                                                                            tranSubsector_name,
                                                                            stubtechnology_name,
                                                                            node.tag,
                                                                        ),
                                                                        year,
                                                                    ]
                                                                )
                                                            else:
                                                                for sub_node in node:
                                                                    if (
                                                                        sub_node.tag
                                                                        in subnode_tag_ls
                                                                    ):

                                                                        sub_node.text = str(
                                                                            data.loc[
                                                                                (
                                                                                    tranSubsector_name,
                                                                                    stubtechnology_name,
                                                                                    sub_node.tag,
                                                                                ),
                                                                                year,
                                                                            ]
                                                                        )
                                                        except:
                                                            pass

    xtree.write(new_file_name, encoding="UTF-8", xml_declaration=True)
