# Author: Jeonghoon Lee
# Date: 2021/12/04

import arcpy
import re

## Setting the arcpy environment from a local path and loading in the oilspills shapefile

arcpy.env.workspace = r'~'

## Objective 6: Creating the ACTUAL_OIL field for later editing with the "Add Field" tool
arcpy.AddField_management("oilspills.shp", "ACTUAL_OIL", "DOUBLE")

## Objective 7: Deleting the PAST_RECO, COMPANY, SYN_TXT fields with the "Delete Field" tool
arcpy.DeleteField_management("oilspills.shp", ["PAST_RECO", "COMPANY", "SYN_TXT"])

## Objective 10: Creating and populating coordinate data (X,Y) fields with the "Add XY" tool
arcpy.AddXY_management("oilspills.shp")

## Creating the update cursor and setting the relevant fields

fields = ["FID", "POSTAL", "MUNI_", "YEAR", "RPT_DTE", "TRCA_ID", "ACTUAL_OIL", "CLEAN_UP", "VOLUME2", "ST_NAME"]

with arcpy.da.UpdateCursor("oilspills.shp", fields) as oilCursor:
    for row in oilCursor:
        
        ## Objective 1: Updating the postal code to a X0X0X0 format
        if len(row[1]) > 6:
            row[1] = row[1].replace("-", "")
            row[1] = row[1].replace(" ", "")

        ## Objective 2: Updating the city names to a current moniker
        if row[2] in ["ETOBICOKE", "NORTH YORK", "YORK", "SCARBOROUGH", "TORONTO CITY", "EAST YORK"]:
            row[2] = "CITY OF TORONTO"

        ## Objective 3: Updating the year to a 19XX format
        if row[3] < 100:
            row[3] = "19" + str(row[3])

        ## Objective 4: Updating the report date to a MM/DD/YYYY format
        if len(row[4]) > 1:
            dateParts = row[4].split("/")
            row[4] = str(dateParts[1]) + "/" + str(dateParts[2]) + "/" + "19" + str(dateParts[0])
        else:
            row[4] = "N/A"

        ## Objective 5: Updating the TRCA ID with sequential integers
        row[5] = row[0] + 1

        ## Objective 6: Populating the ACTUAL_OIL field with CLEAN_UP and VOLUME2
        row[6] = row[7] * row[8] / 100

        ## Objective 8: Modifying the street names from abbreviations to full names using a regex module and a dictionary
        streetName = re.sub("\.", "", row[9])
        streetParts = streetName.split(" ")
        streetDict = {"STREET": "ST", "AVENUE": "AVE", "ROAD": "RD", "DRIVE": "DR", "BOULEVARD": "BLVD", "EAST": "E", "WEST": "W"}
        rev_streetParts = {v:k for k,v in streetDict.items()}
        row[9] = " ".join([rev_streetParts.get(item, item) for item in streetParts])

        oilCursor.updateRow(row)
