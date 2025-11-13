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

Elastic Search indexing reasoning.

Handle a fuzzy search like: "2015 fabrication llc"
and result that corresponds to: year = 2015, make_name = "Fabrication LLC", and maybe model_name = something.

Index the joined view - fetch_canonical_models

 Why joined view instead of separate make, model indices? 
Single search covers all fields (make/model/year). No need for multiple queries or joins in ES. Easy fuzzy search like “2015 ford f150”.

Separate make, model indices: Requires joining or aggregating at query time — Elasticsearch is not built for relational joins, so queries become complicated and slower.


