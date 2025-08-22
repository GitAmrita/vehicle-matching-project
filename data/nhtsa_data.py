import json
import csv
import time
import datetime
from .nhtsa_api import fetch_all_makes, fetch_models_for_make_year

def nhtsa_combine_makes_and_models():
    all_data = []
    makes = fetch_all_makes()
    print(f"✅ Total makes fetched: {len(makes)}")

    current_year = datetime.datetime.now().year
    years = range(1981, current_year + 1)

    for make in makes:
        make_id = make["Make_ID"]
        make_name = make["Make_Name"]

        for year in years:
            print(f"Fetching models for {make_name} ({make_id}) in {year}")
            try:
                models = fetch_models_for_make_year(make_id, year)
                if models:
                    for m in models:
                        all_data.append({
                            "Make_ID": make_id,
                            "Make_Name": make_name,
                            "Model_ID": m.get("Model_ID"),
                            "Model_Name": m.get("Model_Name"),
                            "Year": year
                        })
                # avoid hammering the API
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Error fetching {make_name} ({make_id}) for {year}: {e}")

    # Save JSON
    with open("make_model_year.json", "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"📄 Saved JSON with {len(all_data)} records")

    # Save CSV
    with open("make_model_year.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Make_ID", "Make_Name", "Model_ID", "Model_Name", "Year"])
        writer.writeheader()
        writer.writerows(all_data)
    print(f"📄 Saved CSV with {len(all_data)} records")

    print("🎉 Done!")

if __name__ == "__main__":
    main()
