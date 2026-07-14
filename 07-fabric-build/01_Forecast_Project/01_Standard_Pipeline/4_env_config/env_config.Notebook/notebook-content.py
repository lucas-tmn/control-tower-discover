# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

workspace_name = notebookutils.runtime.context.get('currentWorkspaceName', '')

if workspace_name == 'Enterprise SupplyChain-Dev':
    ENV          = 'dev'
    LAKEHOUSE    = 'SupplyChain_Lakehouse'
    WAREHOUSE    = 'SupplyChain_Warehouse'
    ROW_LIMIT    = None
    LOOKBACK_YRS = 1
elif workspace_name == 'Enterprise SupplyChain':
    ENV          = 'prod'
    LAKEHOUSE    = 'SupplyChain_Lakehouse'
    WAREHOUSE    = 'SupplyChain_Warehouse'
    ROW_LIMIT    = None
    LOOKBACK_YRS = 3
else:
    raise Exception(f"Unknown workspace: '{workspace_name}'")

SCHEMA       = 'dbo'
METADATA_TBL = f'{LAKEHOUSE}.{SCHEMA}.utl_pipeline_metadata'

# Enterprise Lakehouse - fixed, does not change per env
SOURCE_BASE = (
    'abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0'
    '@onelake.dfs.fabric.microsoft.com'
    '/584e7d2c-46ca-49dc-bb6c-68df6ef4f424'
    '/Tables'
)

print(f'ENV={ENV} | Lakehouse={LAKEHOUSE} | Warehouse={WAREHOUSE} | Lookback={LOOKBACK_YRS}yr | Limit={ROW_LIMIT}')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
