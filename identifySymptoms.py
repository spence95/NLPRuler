from __future__ import print_function
import datetime
import os.path
import sys
import re
import mysql.connector
from mysql.connector import errorcode

from rules.Rule import Rule
from rules.identifyDrugYearRules.ContextRule import ContextRule


#def run(records, finalRecords):
def run(rm, records):
    ruids = [
    7,
    10,
    67,
    68,
    69,
    71,
    72,
    74,
    75,
    79,
    80,
    101,
    109,
    119,
    194,
    195,
    196,
    197,
    199,
    200,
    201,
    202,
    203,
    205,
    210,
    212,
    213
    ]
