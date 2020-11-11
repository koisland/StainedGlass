#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mitchell R. Vollger
import os
import sys
import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", help="samid table")
    parser.add_argument("--window", help="window size", type=int, required=True)
    parser.add_argument("--ncolors", help="number of color qauntiles", type=int, default=10)
    parser.add_argument("--fai", help="fai for the genome", required=True)
    parser.add_argument("-d", help="store args.d as true if -d",  action="store_true", default=False)
    args = parser.parse_args()


    df = pd.read_csv(args.infile, sep="\t")
    df.sort_values(by=["query_name",
                       "reference_name",
                       "matches"], inplace=True, ascending=False)
    df.drop_duplicates(subset=["query_name", "reference_name"], inplace=True)
    q_fix = df.query_name.str.extract(r'(.+):(\d+)-\d+', expand=True)
    df.query_name = q_fix[0]
    df.query_start =  q_fix[1].astype(int)
    df.query_end = q_fix[1].astype(int) + args.window

    r_fix = df.reference_name.str.extract(r'(.+):(\d+)-\d+', expand=True)
    df.reference_name = r_fix[0]
    df.reference_start = r_fix[1].astype(int)
    df.reference_end = r_fix[1].astype(int) + args.window
    
    #limit the size
    fai = pd.read_csv(args.fai, sep="\t",names=["chr", "length", "x","y","z"])[["chr","length"]]
    df = pd.merge(df, fai, left_on="query_name", right_on="chr")
    df = pd.merge(df, fai, left_on="reference_name", right_on="chr")
    df.loc[df.query_end >= df.length_x, "length_x"] = df.loc[df.query_end >= df.length_x, "length_x"] - 1 
    df.loc[df.reference_end >= df.length_y, "length_y"] = df.loc[df.reference_end >= df.length_y, "length_y"] - 1 
   
    out=df[["query_name","query_start","query_end","reference_name","reference_start","reference_end","perID_by_events"]]
    out2 = out.copy()
    out2.reference_name = out.query_name
    out2.reference_start = out.query_start
    out2.reference_end = out.query_end
    out2.query_name = out.reference_name
    out2.query_start = out.reference_start
    out2.query_end = out.reference_end

    out=pd.concat([out, out2]).drop_duplicates().sort_values(by=["query_name", "query_start", 
                                                                 "reference_name", "reference_start"])
    out["qcut"] = pd.qcut(out["perID_by_events"], args.ncolors, duplicates="drop", labels=False)
   
    sys.stdout.write("#"+"\t".join(out.columns)+"\n")
    out.to_csv(sys.stdout, index=False, header=False, sep="\t")

