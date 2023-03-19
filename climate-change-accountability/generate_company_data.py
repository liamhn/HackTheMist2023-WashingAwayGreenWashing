import pandas as pd 
import numpy as np 


def parse_net_zero_tracker_data(filename):
    df = pd.read_excel(filename)
    canada = df[df["country"]=="CAN"]
    corporations = canada[canada["actor_type"]=="Company"]
    no_target = corporations[corporations["end_target"] == "No target"]
    no_pledge = corporations[corporations["end_target_status"]=='Proposed / in discussion']
    not_in_strategy = corporations[corporations["end_target_status"]=='Declaration / pledge']
    in_strategy = corporations[corporations["end_target_status"] == "In corporate strategy"]
    return no_target, no_pledge, not_in_strategy, in_strategy


def get_companies_data_by_group(group):
    names = group["name"].tolist()
    for name in names:
        web_scrape(names)

no_target, no_pledge, not_in_strategy, in_strategy = parse_net_zero_tracker_data("net_zero_tracker_canada.xlsx")