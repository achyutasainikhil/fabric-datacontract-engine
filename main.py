import yaml
from pyspark.sql import SparkSession
from soda.scan import Scan
import pandas as pd

# 1. Initialize PySpark session
spark = SparkSession.builder \
    .appName("DataContractLocalPOC") \
    .master("local[*]") \
    .getOrCreate()

print("✅ Spark Session initialized successfully!\n")

# 2. Ingest Sample Data (IBM Telco Churn dataset)
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
pdf = pd.read_csv(url)
pdf.rename(columns={
    'customerID': 'customer_id',
    'tenure': 'tenure_months',
    'MonthlyCharges': 'monthly_charges',
    'TotalCharges': 'total_charges',
    'Churn': 'churn'
}, inplace=True)

df_clean = spark.createDataFrame(pdf[['customer_id', 'tenure_months', 'monthly_charges', 'churn']])

# 3. Validation Engine Class
class FabricDataContractCLI:
    def __init__(self, contract_path: str, spark_session):
        self.spark = spark_session
        with open(contract_path, "r") as f:
            self.contract = yaml.safe_load(f)

    def validate_schema(self, df):
        print("🔍 [1/3] Validating Schema...")
        expected_cols = {col['name'] for col in self.contract['schema']}
        actual_cols = set(df.columns)
        if expected_cols - actual_cols:
            raise ValueError("❌ Schema Validation Failed!")
        print("✅ Schema Validation Passed!")

    def validate_sql_rules(self, temp_table_name: str):
        print("🔍 [2/3] Executing Custom SQL Rules...")
        for rule in self.contract.get('validations', {}).get('sql_rules', []):
            query = rule['query'].replace("{{table}}", temp_table_name)
            result = self.spark.sql(query).collect()[0][0]
            if result != rule['expected']:
                raise AssertionError(f"❌ SQL Rule Failed [{rule['name']}]")
        print("✅ Custom SQL Rules Passed!")

    def validate_soda_quality(self, df, temp_table_name: str):
        print("🔍 [3/3] Executing Soda Core Data Quality Scan...")
        df.createOrReplaceTempView(temp_table_name)
        
        checks_file_path = "soda_checks.yml"
        with open(checks_file_path, "w") as f:
            f.write(self.contract['validations']['soda_checks'])
        
        scan = Scan()
        scan.set_data_source_name("spark_df")
        scan.add_spark_session(self.spark)
        scan.add_sodacl_yaml_file(checks_file_path)
        scan.execute()
        
        if scan.has_check_fails():
            raise AssertionError("❌ Soda Data Quality Violations Detected!")
        print("✅ Soda Data Quality Checks Passed!")

    def run_full_contract_check(self, df, temp_table_name: str):
        self.validate_schema(df)
        self.validate_sql_rules(temp_table_name)
        self.validate_soda_quality(df, temp_table_name)
        print("🎉 ALL DATA CONTRACT CHECKS PASSED SUCCESSFULLY!\n")

# --- EXECUTE DEMO SCENARIOS ---
cli = FabricDataContractCLI("datacontract.yaml", spark)

print("--- DEMO 1: Clean Data (Should Pass) ---")
df_clean.createOrReplaceTempView("temp_gold_customer_churn")
cli.run_full_contract_check(df_clean, "temp_gold_customer_churn")

print("--- DEMO 2: Corrupted Data Injection (Should Block Pipeline) ---")
dirty_data = [("1234-BAD", -5, -99.0, "No"), ("1234-BAD", 12, 50.0, "Yes")]
df_corrupted = df_clean.union(spark.createDataFrame(dirty_data, ["customer_id", "tenure_months", "monthly_charges", "churn"]))
df_corrupted.createOrReplaceTempView("temp_corrupted_churn")

try:
    cli.run_full_contract_check(df_corrupted, "temp_corrupted_churn")
except Exception as e:
    print(f"🛡️ Guardrail Action Triggered Successfully: {e}")