his project builds a pipeline to match vendor vehicle strings to canonical Year-Make-Model records.

Step 1: 
NHTSA api
First fetch all makes:
https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json
Gives Make_ID and Make_Name.

Loop over years (1981 → current) and make IDs.
https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeIdYear/makeId/440/modelyear/2015?format=json
Save all Make_ID, Make_Name, Model_ID, Model_Name, Year.
