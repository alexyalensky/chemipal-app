import os
import time
import threading
import random
from datetime import datetime
from dotenv import load_dotenv

from HitoAPI import *
from INVORD import *
from PreNames import *
from OrdFunctions import *
from InvFunctions import *
from FitemFunctions import *
from helpers import (entity2entity, entity_param_2_entity_param, entity_param_2_entity_param_by_criteria, 
                     change_param_value_based_on_another_param_is_not_empty, transfer_volunteers, 
                     entity_2_users_delek, transfer_records, transfer_records_based_on_blocks)
from OrderNumbering import *
from check_volunteer_exists import *
from PulseemAPI import *
import requests
from g1_functions import create_users_from_entity_rows
from logging_config import setup_logging, get_logger

load_dotenv()

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)

chemipal = HitoAPI(os.environ.get("CHEMIPAL_DOMAIN"), os.environ.get("CHEMIPAL_API_KEY"))
rlz = HitoAPI(os.environ.get("RLZ_DOMAIN"), os.environ.get("RLZ_API_KEY"))
delek = HitoAPI(os.environ.get("DELEK_DOMAIN"), os.environ.get("DELEK_API_KEY"))
netanya = HitoAPI(os.environ.get("NETANYA_DOMAIN"), os.environ.get("NETANYA_API_KEY"))
holon = HitoAPI(os.environ.get("HOLON_DOMAIN"), os.environ.get("HOLON_API_KEY"))
namal = HitoAPI(os.environ.get("NAMAL_DOMAIN"), os.environ.get("NAMAL_API_KEY"))
ashdod = HitoAPI(os.environ.get("ASHDOD_DOMAIN"), os.environ.get("ASHDOD_API_KEY"))
g1 = HitoAPI(os.environ.get("G1_DOMAIN"), os.environ.get("G1_API_KEY"))

def g1_processes():
    while True:
        logger.info('START: g1_processes - every 1 minute')
        create_users_from_entity_rows(g1, 34, [{"paramId": 989, "operator": "EQ", "values": [2]}], [574, 575, 627, 628, 570, 629, 580, 581, 582, 583, 584, 585, 822])
        logger.info('END: g1_processes')
        time.sleep(60)

def ashdod_betihut():
    while True:
        logger.info('START: ashdod_betihut - every 10 minutes')
        transfer_records(
            customer_name="Ashdod",
            api=ashdod,
            origin_entity_id=240,
            dest_entity_id=119,
            search_criteria=[{"paramId": 4383, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[4299, 4301, 4302, 4305, 4323, 4324],
            param_ids_to_receive=[2184, 2185, 2186, 2190, 4296, 4297],
            program_status_param_id=4383, new_id_pos=0
        )

        transfer_records(
            customer_name="Ashdod",
            api=ashdod,
            origin_entity_id=228,
            dest_entity_id=119,
            search_criteria=[{"paramId": 4382, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[4067, 4073, 4074, 4141, 4144, 4142, 4069],
            param_ids_to_receive=[2184, 2185, 2186, 2190, 4297, 4296, 4146],
            program_status_param_id=4382, new_id_pos=0
        )
        logger.info('END: ashdod_betihut')
        time.sleep(600)


def namal_proccesses():
    while True:
        logger.info('START: namal_proccesses - every 1 minute')
        transfer_records(
            customer_name="NAMAL", api=namal, origin_entity_id=105, dest_entity_id=62,
            search_criteria=[{"paramId": 1872, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[1721, 1743, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688,
                                   1689, 1690, 1691, 1902, 1693, 1694, 1695, 1696, 1697, 1698, 1700, 1701, 1702, 1703,
                                   1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717,
                                   1718, 1719, 1720, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1841, 1730, 1731, 1738,
                                   1739, 1740, 1741, 1742, 1843],
            param_ids_to_receive=[901, 1503, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871,
                                  1903, 873, 874, 875, 876, 877, 878, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889,
                                  890, 891, 892, 893, 1671, 894, 895, 896, 897, 898, 900, 962, 996, 997, 998, 1093,
                                  1095, 1096, 1122, 1147, 1148, 1157, 1161, 1477, 1478, 1479, 1842],
            program_status_param_id=1872, new_id_pos=0)
        transfer_records_based_on_blocks(
            customer_name="NAMAL",
            api=namal,
            origin_entity_id=106,
            dest_entity_id=102,
            search_criteria=[{"paramId": 1871, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[1746, 1745, 1771, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757,
                                   1758,
                                   1759],
            param_ids_to_receive=[1579, 1581, 1773, 1582, 1576, 1584, 1577, 1578, 1583, 1586, 1585, 1580, 1587, 1588,
                                  1589,
                                  1590],
            program_status_param_id=1871,
            block_param_pos=4,
            new_id_pos=0
        )
        logger.info('END: namal_proccesses')
        time.sleep(60)


def volunteer_processes():
    while True:
        logger.info('START: volunteer_processes - every 1 hour')
        transfer_volunteers(
            customer_name="RLZ",
            api=rlz,
            origin_entity_id=31,
            dest_entity_id=187,
            search_criteria=[{"paramId": 4592, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[532, 524, 529, 530, 535, 536, 537, 538, 539, 531, 903, 533, 534, 540, 3648, 2765],
            param_ids_to_receive=[4238, 4229, 4235, 4236, 4242, 4243, 4244, 4245, 4246, 4237, 4239, 4240, 4241, 4247,
                                  4248, 4510],
            program_status_param_id=4592,
            update_origin_entity_with_tz_without_zero_param=4421)
        transfer_volunteers(
            customer_name="NETANYA",
            api=netanya,
            origin_entity_id=223,
            dest_entity_id=222,
            search_criteria=[{"paramId": 5294, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[5263, 5262, 5271, 5264, 5279, 5298, 5309, 5310, 5274, 5280, 5281, 5282, 5283, 5311],
            param_ids_to_receive=[5063, 5064, 5065, 5060, 5074, 5073, 5328, 5329, 5070, 5077, 5361, 5362, 5363, 5365],
            program_status_param_id=5294,
            update_origin_entity_with_tz_without_zero_param=5270)
        transfer_volunteers(
            customer_name="HOLON",
            api=holon,
            origin_entity_id=137,
            dest_entity_id=142,
            search_criteria=[{"paramId": 2687, "operator": "EQ", "values": [1]}],
            param_ids_to_transfer=[2248, 2246, 2247, 2493, 2495, 2249, 2250, 2251, 2269, 2253, 2252, 2254, 2255, 2256,
                                   2491, 2490,
                                   2259, 2262, 2263, 2776, 2402, 3027, 2947, 2777],
            param_ids_to_receive=[2688, 2358, 2359, 2389, 2395, 2361, 2362, 2363, 2364, 2366, 2365, 2367, 2368, 2369,
                                  2424, 2425,
                                  2426, 2429, 2430, 2385, 2392, 3026, 3118, 2390],
            program_status_param_id=2687,
            update_origin_entity_with_tz_without_zero_param=2457)
        logger.info('END: volunteer_processes')
        time.sleep(3601)


def delek_processes():
    while True:
        logger.info('START: delek_processes - every 2 hours')
        entity_2_users_delek(
            api=delek,
            entity_id=2,
            criteria_param_id=376,
            criteria_value="1",
            criteria_value_id_after_move_to_user=2,
            entity_params_to_transfer=[11, 12, 308, 25, 217, 147, 380, 317, 376]
        )
        logger.info('END: delek_processes')
        time.sleep(7202)


def main_processes():
    while True:
        logger.info('START: main_processes - every 7 minutes')
        inv_file_import = PreNames("INV", 8, chemipal, os.environ.get("SOURCE_FOLDER"),
                                   os.environ.get("DESTINATION_FOLDER"))
        new_inv_files_imported = inv_file_import.creating_body_to_update_with_new_id_INV_FITEM()
        if new_inv_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=8,
                origin_param_id_to_find=250,
                dest_param_id_to_find=609,
                origin_param_id_to_transfer=3,
                dest_param_id_to_recieve=707
            )
        del inv_file_import
        fitem_file_import = PreNames("FITEM", 1, chemipal, os.environ.get("SOURCE_FOLDER"),
                                     os.environ.get("DESTINATION_FOLDER"))
        new_fitem_files_imported = fitem_file_import.creating_body_to_update_with_new_id_INV_FITEM()
        if new_fitem_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=8,
                origin_param_id_to_find=250,
                dest_param_id_to_find=609,
                origin_param_id_to_transfer=3,
                dest_param_id_to_recieve=707
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=5,
                dest_entity_id=1,
                origin_param_id_to_find=47,
                dest_param_id_to_find=1,
                origin_param_id_to_transfer=48,
                dest_param_id_to_recieve=49
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=6,
                dest_entity_id=1,
                origin_param_id_to_find=52,
                dest_param_id_to_find=20,
                origin_param_id_to_transfer=283,
                dest_param_id_to_recieve=281
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=6,
                dest_entity_id=1,
                origin_param_id_to_find=52,
                dest_param_id_to_find=20,
                origin_param_id_to_transfer=244,
                dest_param_id_to_recieve=282
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=4,
                dest_entity_id=1,
                origin_param_id_to_find=42,
                dest_param_id_to_find=16,
                origin_param_id_to_transfer=41,
                dest_param_id_to_recieve=192
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=21,
                dest_entity_id=1,
                origin_param_id_to_find=248,
                dest_param_id_to_find=272,
                origin_param_id_to_transfer=247,
                dest_param_id_to_recieve=269
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=35,
                dest_entity_id=1,
                origin_param_id_to_find=494,
                dest_param_id_to_find=490,
                origin_param_id_to_transfer=493,
                dest_param_id_to_recieve=491
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=36,
                dest_entity_id=1,
                origin_param_id_to_find=496,
                dest_param_id_to_find=488,
                origin_param_id_to_transfer=497,
                dest_param_id_to_recieve=489
            )
        del fitem_file_import
        fitem_functions = FitemFunctions(chemipal)
        fitem_functions.check_for_new_fitem_rows()
        fitem_functions.validate_fitem_rows()
        new_fitem_records = entity2entity(
            api=chemipal,
            origin_entity_id=28,
            dest_entity_id=1,
            search_criteria=[{"paramId": 702, "operator": "EQ", "values": ["5"]}],
            param_ids_to_transfer=[340, 341, 342, 343, 344, 345, 644, 347, 348, 484, 485, 350, 351, 352, 353, 354, 355,
                                   356, 357, 358, 486, 487, 360],
            param_ids_to_receive=[3, 4, 16, 17, 192, 15, 250, 272, 269, 488, 489, 39, 7, 8, 20, 281, 282, 10, 11, 40,
                                  490, 491, 13],
            program_status_param_id=702
        )
        if new_fitem_records:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=8,
                origin_param_id_to_find=250,
                dest_param_id_to_find=609,
                origin_param_id_to_transfer=3,
                dest_param_id_to_recieve=707
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=5,
                dest_entity_id=1,
                origin_param_id_to_find=47,
                dest_param_id_to_find=1,
                origin_param_id_to_transfer=48,
                dest_param_id_to_recieve=49
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=6,
                dest_entity_id=1,
                origin_param_id_to_find=52,
                dest_param_id_to_find=20,
                origin_param_id_to_transfer=283,
                dest_param_id_to_recieve=281
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=6,
                dest_entity_id=1,
                origin_param_id_to_find=52,
                dest_param_id_to_find=20,
                origin_param_id_to_transfer=244,
                dest_param_id_to_recieve=282
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=4,
                dest_entity_id=1,
                origin_param_id_to_find=42,
                dest_param_id_to_find=16,
                origin_param_id_to_transfer=41,
                dest_param_id_to_recieve=192
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=21,
                dest_entity_id=1,
                origin_param_id_to_find=248,
                dest_param_id_to_find=272,
                origin_param_id_to_transfer=247,
                dest_param_id_to_recieve=269
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=35,
                dest_entity_id=1,
                origin_param_id_to_find=494,
                dest_param_id_to_find=490,
                origin_param_id_to_transfer=493,
                dest_param_id_to_recieve=491
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=36,
                dest_entity_id=1,
                origin_param_id_to_find=496,
                dest_param_id_to_find=488,
                origin_param_id_to_transfer=497,
                dest_param_id_to_recieve=489
            )
        del fitem_functions
        inv_functions = InvFunctions(chemipal)
        inv_functions.check_for_new_inv_rows()
        inv_functions.validate_inv_rows()
        del inv_functions
        inv_order_numbering = OrderNumbering(
            api=chemipal,
            entity_num=33,
            numbering_param_id=461,
            order_num_param_id=460,
            sapak_name=458,
            date_pickup=459,
            status_param_id=701,
            status_value_id=5,
            searchCriteria=[
                {
                    "paramId": 525,
                    "operator": "EQ",
                    "values": ["1"]
                }
            ]
        )
        inv_order_numbering.start()
        del inv_order_numbering
        new_inv_records = entity2entity(
            api=chemipal,
            origin_entity_id=33,
            dest_entity_id=8,
            search_criteria=[{"paramId": 701, "operator": "EQ", "values": ["5"]}],
            param_ids_to_transfer=[458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 700],
            param_ids_to_receive=[62, 71, 72, 88, 64, 75, 73, 77, 78, 79, 86, 708],
            program_status_param_id=701
        )
        if new_inv_records:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=9,
                dest_entity_id=8,
                origin_param_id_to_find=89,
                dest_param_id_to_find=60,
                origin_param_id_to_transfer=95,
                dest_param_id_to_recieve=513
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=9,
                dest_entity_id=8,
                origin_param_id_to_find=89,
                dest_param_id_to_find=60,
                origin_param_id_to_transfer=92,
                dest_param_id_to_recieve=71
            )
            entity_param_2_entity_param_by_criteria(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=518,
                dest_param_id_to_recieve=102,
                search_criteria=[{
                    "paramId": 102,
                    "operator": "EQ",
                    "values": ["2"]
                }]
            )
            entity_param_2_entity_param_by_criteria(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=8,
                origin_param_id_to_find=225,
                dest_param_id_to_find=513,
                origin_param_id_to_transfer=226,
                dest_param_id_to_recieve=584,
                search_criteria=[
                    {"paramId": 584, "operator": "E"},
                    {"paramId": 528, "operator": "EQ", "values": [1]}
                ]
            )
            change_param_value_based_on_another_param_is_not_empty(
                api=chemipal,
                entity_id=8,
                dest_param={"id": 628, "valueId": 3},
                search_criteria=[{"paramId": 584, "operator": "NE"}, {"paramId": 628, "operator": "E"}]
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=8,
                origin_param_id_to_find=49,
                dest_param_id_to_find=73,
                origin_param_id_to_transfer=1,
                dest_param_id_to_recieve=582
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=8,
                origin_param_id_to_find=49,
                dest_param_id_to_find=73,
                origin_param_id_to_transfer=250,
                dest_param_id_to_recieve=609
            )
        ord_functions = OrdFunctions(chemipal)
        ord_functions.check_for_new_reference()
        ord_functions.check_for_new_ord_rows()
        ord_functions.ord_temp_reference()
        ord_functions.validate_ord_rows()
        ord_functions.update_ask_ord_in_inv()
        del ord_functions
        ord_order_numbering = OrderNumbering(
            api=chemipal,
            entity_num=34,
            numbering_param_id=474,
            order_num_param_id=472,
            sapak_name=471,
            date_pickup=473,
            status_param_id=691,
            status_value_id=5,
            searchCriteria=[
                {
                    "paramId": 477,
                    "operator": "EQ",
                    "values": ["2"]
                }
            ]
        )
        ord_order_numbering.start()
        new_ord_records = entity2entity(
            api=chemipal,
            origin_entity_id=34,
            dest_entity_id=10,
            search_criteria=[{"paramId": 691, "operator": "EQ", "values": ["5"]}],
            param_ids_to_transfer=[471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 690],
            param_ids_to_receive=[97, 147, 98, 99, 100, 101, 102, 176, 230, 231, 483, 693],
            program_status_param_id=691
        )
        if new_ord_records:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=226,
                dest_param_id_to_recieve=230
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=228,
                dest_param_id_to_recieve=231
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=8,
                dest_entity_id=10,
                origin_param_id_to_find=513,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=582,
                dest_param_id_to_recieve=583
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=10,
                origin_param_id_to_find=1,
                dest_param_id_to_find=583,
                origin_param_id_to_transfer=3,
                dest_param_id_to_recieve=697
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=10,
                origin_param_id_to_find=1,
                dest_param_id_to_find=583,
                origin_param_id_to_transfer=250,
                dest_param_id_to_recieve=699
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=1,
                dest_entity_id=10,
                origin_param_id_to_find=1,
                dest_param_id_to_find=583,
                origin_param_id_to_transfer=489,
                dest_param_id_to_recieve=698
            )
        del ord_order_numbering
        logger.info('END: main_processes')
        time.sleep(421)


def thirty_min():
    while True:
        logger.info('START: thirty_min')
        spk_file_import = PreNames("SPK", 4, chemipal, os.environ.get("SOURCE_FOLDER"),
                                   os.environ.get("DESTINATION_FOLDER"))
        new_spk_files_imported = spk_file_import.creating_body_to_update()
        if new_spk_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=4,
                dest_entity_id=1,
                origin_param_id_to_find=42,
                dest_param_id_to_find=16,
                origin_param_id_to_transfer=41,
                dest_param_id_to_recieve=192
            )
        del spk_file_import
        itm_file_import = PreNames("ITM", 5, chemipal, os.environ.get("SOURCE_FOLDER"),
                                   os.environ.get("DESTINATION_FOLDER"))
        new_itm_files_imported = itm_file_import.creating_body_to_update()
        if new_itm_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=5,
                dest_entity_id=1,
                origin_param_id_to_find=47,
                dest_param_id_to_find=1,
                origin_param_id_to_transfer=48,
                dest_param_id_to_recieve=49
            )
        del itm_file_import
        ctr_file_import = PreNames("CTR", 7, chemipal, os.environ.get("SOURCE_FOLDER"),
                                   os.environ.get("DESTINATION_FOLDER"))
        ctr_file_import.creating_body_to_update()
        del ctr_file_import
        logger.info('END: thirty_min')
        time.sleep(1800)


def one_hour():
    while True:
        logger.info('START: one_hour')
        inv_file_export = INVORD(chemipal, 8)
        inv_file_export.start()
        del inv_file_export
        logger.info('END: one_hour')
        time.sleep(3600)


def fifteen_min():
    while True:
        logger.info('START: fifteen_min')
        doc_file_import = PreNames("DOC", 19, chemipal, os.environ.get("SOURCE_FOLDER"),
                                   os.environ.get("DESTINATION_FOLDER"))
        new_doc_files_imported = doc_file_import.creating_body_to_update_with_new_id()
        if new_doc_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=226,
                dest_param_id_to_recieve=230
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=228,
                dest_param_id_to_recieve=231
            )
            entity_param_2_entity_param_by_criteria(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=10,
                origin_param_id_to_find=225,
                dest_param_id_to_find=101,
                origin_param_id_to_transfer=518,
                dest_param_id_to_recieve=102,
                search_criteria=[{
                    "paramId": 102,
                    "operator": "EQ",
                    "values": ["2"]
                }]
            )
            entity_param_2_entity_param_by_criteria(
                api=chemipal,
                origin_entity_id=19,
                dest_entity_id=8,
                origin_param_id_to_find=225,
                dest_param_id_to_find=513,
                origin_param_id_to_transfer=226,
                dest_param_id_to_recieve=584,
                search_criteria=[
                    {"paramId": 584, "operator": "E"},
                    {"paramId": 528, "operator": "EQ", "values": [1]}
                ]
            )
            change_param_value_based_on_another_param_is_not_empty(
                api=chemipal,
                entity_id=8,
                dest_param={"id": 628, "valueId": 3},
                search_criteria=[{"paramId": 584, "operator": "NE"}, {"paramId": 628, "operator": "E"}]
            )
        del doc_file_import
        rinv_file_import = PreNames("RINV", 9, chemipal, os.environ.get("SOURCE_FOLDER"),
                                    os.environ.get("DESTINATION_FOLDER"))
        new_rinv_files_imported = rinv_file_import.creating_body_to_update()
        if new_rinv_files_imported:
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=9,
                dest_entity_id=8,
                origin_param_id_to_find=89,
                dest_param_id_to_find=60,
                origin_param_id_to_transfer=95,
                dest_param_id_to_recieve=513
            )
            entity_param_2_entity_param(
                api=chemipal,
                origin_entity_id=9,
                dest_entity_id=8,
                origin_param_id_to_find=89,
                dest_param_id_to_find=60,
                origin_param_id_to_transfer=92,
                dest_param_id_to_recieve=71
            )
        del rinv_file_import
        ord_file_export = INVORD(chemipal, 10)
        ord_file_export.start()
        del ord_file_export
        logger.info('END: fifteen_min')
        time.sleep(901)


thread_all = threading.Thread(target=main_processes)
thread_thirty_min = threading.Thread(target=thirty_min)
thread_one_hour = threading.Thread(target=one_hour)
thread_fifteen_min = threading.Thread(target=fifteen_min)
thread_volunteer_processes = threading.Thread(target=volunteer_processes)
thread_delek_processes = threading.Thread(target=delek_processes)
thread_namal = threading.Thread(target=namal_proccesses)
thread_ashdod = threading.Thread(target=ashdod_betihut)
thread_g1 = threading.Thread(target=g1_processes)

thread_all.start()
thread_thirty_min.start()
thread_one_hour.start()
thread_fifteen_min.start()
thread_volunteer_processes.start()
thread_delek_processes.start()
thread_namal.start()
thread_ashdod.start()
thread_g1.start()

thread_all.join()
thread_thirty_min.join()
thread_one_hour.join()
thread_fifteen_min.join()
thread_volunteer_processes.join()
thread_delek_processes.join()
thread_namal.join()
thread_ashdod.join()
thread_g1.join()
