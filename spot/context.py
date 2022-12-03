import os
import subprocess
import json
import pandas as pd
import numpy as np

from spot.constants import *


class Context:
    def __init__(self):
        self.invocation_df = pd.DataFrame()
        self.pricing_df = pd.DataFrame()
        self.final_df = None

    def save_invocation_result(self, result_df):
        self.invocation_df = pd.concat([self.invocation_df, result_df])

    def save_final_result(self, final_df):
        self.final_df = final_df

    def record_pricing(self, row):
        df = pd.DataFrame(row)
        self.pricing_df = pd.concat([self.pricing_df, df])

    def save_supplemantary_info(self, function_name: str, optimization_s):
        self.final_df["Benchmark Name"] = function_name
        self.final_df["Alpha"] = ALPHA
        self.final_df["Normal Scale"] = NORMAL_SCALE
        self.final_df["Sample Count"] = TOTAL_SAMPLE_COUNT
        self.final_df["Termination CV"] = TERMINATION_CV
        self.final_df["Knowledge Ratio"] = KNOWLEDGE_RATIO
        self.final_df["Dynamic Sampling Max"] = DYNAMIC_SAMPLING_MAX
        self.final_df["Dynamic Sampling Initial Step"] = DYNAMIC_SAMPLING_INITIAL_STEP
        if optimization_s:
            self.final_df["Time Elapsed in Seconds"] = optimization_s

        self.invocation_df["Benchmark Name"] = function_name
        self.invocation_df["Alpha"] = ALPHA
        self.invocation_df["Normal Scale"] = NORMAL_SCALE
        self.invocation_df["Sample Count"] = TOTAL_SAMPLE_COUNT
        self.invocation_df["Termination CV"] = TERMINATION_CV
        self.invocation_df["Knowledge Ratio"] = KNOWLEDGE_RATIO
        self.invocation_df["Dynamic Sampling Max"] = DYNAMIC_SAMPLING_MAX
        self.invocation_df[
            "Dynamic Sampling Initial Step"
        ] = DYNAMIC_SAMPLING_INITIAL_STEP