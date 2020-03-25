import pandas as pd         # Pandas is how we handle data in Python
import numpy as np          # Access to python's scientific computing library
import scipy                # Modules for mathematics, science, and engineering
import os                   # Access to operating system commands
import requests             # Access to HTTPS commands to retrieve data
import getpass              # Access to secure handling of sensitive values (i.e. passwords, API keys)
from datetime import date, timedelta # Access to current date and time operations
import time                 # Time helper functions
import arcgis               # Access to spatially-enabled dataframe
import arcpy                # Access to ArcGIS Pro geoprocessing tools 

class Toolbox(object):
    def __init__(self):
        self.label = "COVID-19 Data Retrieval Tools"
        self.alias = "covid19"
        self.tools = [GetCOVID19TestingData_mostRecent]

class GetCOVID19TestingData_mostRecent(object):

    def __init__(self):
        self.label = "Get Today's State Testing Data"
        self.description = "Uses data from the COVID-19 tracking project to generate a feature class of the most recent daily testing per state in the United States."
        self.canRunInBackground = True

    def getParameterInfo(self):
        # Define parameter definitions

        out_featureclass = arcpy.Parameter(
            displayName="Output Feature Class",
            name="out_featureclass",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        out_featureclass.value = os.path.join(arcpy.mp.ArcGISProject("CURRENT").defaultGeodatabase, "covid19_testing_"+date.today().strftime("%Y%m%d"))

        in_calculate_testing_rate = arcpy.Parameter(
            displayName="Calculate Tests Per Million People",
            name="in_calc_testing_rate",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        in_calculate_testing_rate.value = True

        in_enrich_with_age_breakouts = arcpy.Parameter(
            displayName="Enrich With Age Breakouts",
            name="in_enrich_age",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        in_enrich_with_age_breakouts.value = False  

        in_add_state_grade_layer = arcpy.Parameter(
            displayName="Include Test Data Grade Layer",
            name="in_add_state_grade_layer",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        in_add_state_grade_layer.value = False        


        parameters = [out_featureclass, in_calculate_testing_rate, in_enrich_with_age_breakouts, in_add_state_grade_layer]

        return parameters

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        
        # Instantiate parameters
        out_featureclass = parameters[0].valueAsText
        in_calculate_testing_rate = parameters[1].value
        in_enrich_with_age_breakouts = parameters[2].value
        in_add_state_grade_layer = parameters[3].value

        ### Retrieve testing data ###
        arcpy.AddMessage("Retrieving most recent data from covidtracking.com API...")
        api_url = r"https://covidtracking.com/api/states"
        r = requests.get(url = api_url)
        data = r.json()
        tests_df = pd.DataFrame(data)

        ### Append geometry ###
        gis = arcgis.gis.GIS()
        # Search for USA_Counties
        search = gis.content.search("USA States", item_type="feature_service", outside_org=True, sort_field="numViews")
        # Use the correct index to reference the search result
        states_item = search[0]
        # Read the layer into a dataframe
        states_df = states_item.layers[0].query().sdf
        if in_enrich_with_age_breakouts:
            states_df = states_df[['FID', 
                                   'STATE_NAME', 
                                   'STATE_FIPS', 
                                   'SUB_REGION', 
                                   'STATE_ABBR', 
                                   'POPULATION',
                                   'AGE_5_9', 
                                   'AGE_10_14', 
                                   'AGE_15_19', 
                                   'AGE_20_24', 
                                   'AGE_25_34', 
                                   'AGE_35_44', 
                                   'AGE_45_54', 
                                   'AGE_55_64', 
                                   'AGE_65_75', 
                                   'AGE_75_84',
                                   'AGE_85_UP',
                                   'SHAPE']]
        else:
            states_df = states_df[['FID', 
                                   'STATE_NAME', 
                                   'STATE_FIPS', 
                                   'SUB_REGION', 
                                   'STATE_ABBR', 
                                   'POPULATION', 
                                   'SHAPE']]
        
        # Join the geometry data to our testing data table
        geo_df = pd.merge(states_df, tests_df, left_on='STATE_ABBR', right_on='state', how='left')

        # Calculate testing rate
        if in_calculate_testing_rate:
            geo_df['tests_per_1M_residents'] = geo_df['total'] / (geo_df['POPULATION'] / 1000000)

        # Add the feature class to current project and symbolize
        pro_project = arcpy.mp.ArcGISProject("CURRENT")
        pro_map = pro_project.listMaps(pro_project.activeMap.name)[0]

        # Export the spatially-enabled dataframe to a feature class
        arcpy.AddMessage("Exporting feature class...")
        out_fc = geo_df.spatial.to_featureclass(location=out_featureclass)

        # Add state grade layer if necessary
        if in_add_state_grade_layer:
            out_grade_layer = pro_map.addDataFromPath(out_fc)
            symb_layer = r"covid19_testing_grade.lyrx"
            arcpy.management.ApplySymbologyFromLayer(out_grade_layer, 
                                                     symb_layer, 
                                                     "VALUE_FIELD score score", "MAINTAIN")

            # Workaround to apply symbology layer to output layer
            arcpy.SaveToLayerFile_management(out_grade_layer, r"templayer_grade.lyr", "RELATIVE")
            grade_lyr_file = arcpy.mp.LayerFile(r"templayer_grade.lyrx")
            grade_lyr = grade_lyr_file.listLayers()[0]
            old_lyr_name = out_grade_layer.name
            grade_lyr.updateConnectionProperties(grade_lyr.connectionProperties, out_grade_layer.connectionProperties)
            grade_lyr.name = old_lyr_name
            grade_lyr.name = "COVID-19 Testing Data Grade: "+date.today().strftime("%b %d, %Y")
            grade_lyr_file.save()
            grade_lyr_file.visible = True
            pro_map.insertLayer(out_grade_layer, grade_lyr_file)
            pro_map.removeLayer(out_grade_layer)

        # Add Test Rates Layer
        out_layer = pro_map.addDataFromPath(out_fc)
        symb_layer = r"covid19_testing.lyrx"
        arcpy.management.ApplySymbologyFromLayer(out_layer, 
                                                 symb_layer, 
                                                 "VALUE_FIELD tests_per_1M_residents tests_per_1M_residents", "MAINTAIN")

        # Workaround to apply symbology layer to output layer
        arcpy.SaveToLayerFile_management(out_layer, r"templayer.lyr", "RELATIVE")
        new_lyr_file = arcpy.mp.LayerFile(r"templayer.lyrx")
        new_lyr = new_lyr_file.listLayers()[0]
        old_lyr_name = out_layer.name
        new_lyr.updateConnectionProperties(new_lyr.connectionProperties, out_layer.connectionProperties)
        new_lyr.name = old_lyr_name
        new_lyr.name = "COVID-19 Testing: "+date.today().strftime("%b %d, %Y")
        new_lyr_file.save()
        new_lyr_file.visible = True
        pro_map.insertLayer(out_layer, new_lyr_file)
        pro_map.removeLayer(out_layer)
        

        arcpy.AddMessage("Data download completed.")
        return

