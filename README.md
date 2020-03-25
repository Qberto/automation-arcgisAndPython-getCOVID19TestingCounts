# automation-arcgisAndPython-getCOVID19TestingCounts
 
## Description
This ArcGIS Pro project package contains a geoprocessing tool and accompanying notebook to allow GIS users to retrieve daily data for COVID-19 tests per state in the United States using data from the COVID Tracking Project.

## Data Context:
The [COVID Tracking Project](https://covidtracking.com/) collects information from 50 US states, the District of Columbia, and 5 other US territories to provide comprehensive testing data for the novel coronavirus, SARS-CoV-2. The dataset attempts to include positive and negative results, pending tests, and total people tested for each state or district currently reporting that data.

## Guide:
Download the package found at **gis/pro_project/Package/COVID19_GetTestingData.ppkx** locally and open. Once opened, you should see a screen that looks like the following:
![](https://github.com/Qberto/automation-arcgisAndPython-getCOVID19TestingCounts/blob/master/media/ProProject01.JPG?raw=true)

Open the Catalog Pane, then expand the Toolboxes entry. The download tool is available within the COVID19 Get Testing Data Tools.pyt python toolbox. Open the Get Today's State Testing Data tool:
![](https://github.com/Qberto/automation-arcgisAndPython-getCOVID19TestingCounts/blob/master/media/ProProject02.JPG?raw=true)

## The tool has three parameters:
![](https://github.com/Qberto/automation-arcgisAndPython-getCOVID19TestingCounts/blob/master/media/ProProject03.JPG?raw=true)
* Output Feature Class (Path): The path to a feature class where the current day's state testing data will be written. The default value of this parameter is "covid19_testing_" and a timestamp for today's date in the format YYYYMMDD. 
* Calculate Tests Per Million People (Boolean): If checked, the tool will produce an additional field in the output composed of total tests for the state divided by the state's 2019 population. 
* Enrich With Age Breakouts (Boolean): If checked, the tool will include fields pertaining to the state's population at several age ranges in five-year increments. 
* Include Test Data Grade Layer (Boolean): If checked, the tool will produce an additional output layer in the current map composed which symbolizes each state's data quality grade, using the grading schema established by the COVID Tracking Project.

## Supplemental Jupyter Notebook 
![](https://github.com/Qberto/automation-arcgisAndPython-getCOVID19TestingCounts/blob/master/media/ProProject04.JPG?raw=true)

The ArcGIS Pro project also includes a Jupyter Notebook containing the code used by the geoprocessing tool. You may open and directly execute the cells in this notebook, or use it to test changes and further customization of this download process. To open the notebook (ArcGIS Pro 2.5 required), use the Catalog Pane, then expand the current folder connection, and double-click the COVID19_TestingData_Processing.ipynb file:
![](https://github.com/Qberto/automation-arcgisAndPython-getCOVID19TestingCounts/blob/master/media/ProProject05.JPG?raw=true)