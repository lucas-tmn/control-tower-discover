# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Fabric notebook source
# Notebook: nb_dq_after_brz
# Purpose: Run DQ checks for BRZ layer
# Called by: pl_master_daily (after pl_brz_daily)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Cell 1 — Execute DQ Engine with BRZ parameter

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

notebookutils.notebook.run("nb_dq_engine", 900, {"DQ_LAYER": "BRZ"})

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
