his project builds a pipeline to match vendor vehicle strings to canonical Year-Make-Model records.

Step 1: 
NHTSA dataset
First fetch all makes:
https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json
Gives Make_ID and Make_Name.

Loop over years (1981 → current) and make IDs.
https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeIdYear/makeId/440/modelyear/2015?format=json
Save all Make_ID, Make_Name, Model_ID, Model_Name, Year.

EPA FuelEconomy.gov Dataset

Get all vehicle makes for a year:
https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year=2015
Gives Make_name, Year

Get all models for a make + year:
https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year=2015&make=Honda
Gives model_name, Year

Set up Elastic search

cd /Users/amy/Documents/Code/vehicle-matching-project
docker-compose up -d

# Test connection
curl http://localhost:9200

Kibana Dev Tools will be available at: http://localhost:5601
