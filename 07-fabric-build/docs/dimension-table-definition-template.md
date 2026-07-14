---
title: <TableName> table documentation
domain: <Business Domain>  
warehouse: 
schema: <schema> 
table_name: <TableName> 
last_updated: <YYYY-MM-DD>  
owner: <Owner / Team>  

---

## 1. Purpose & Business Context

<One to three sentences describing what this table stores and why it exists.>

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.<table_name> (
    <ColumnName> <DATA_TYPE> NOT NULL,
    <ColumnName> <DATA_TYPE> NOT NULL,
    <ColumnName> <DATA_TYPE> NOT NULL
);
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `<ColumnName>` | `<DataType>` | `<Notes>` |
| `<ColumnName>` | `<DataType>` | `<Notes>` |
| `<ColumnName>` | `<DataType>` | `<Notes>` |

---

## 4. Source Data & ETL Logic (Optional)

```tsql
-- Load dimension from source table(s)
INSERT INTO <warehouse>.<schema>.<table_name>
(
    <ColumnName>,
    <ColumnName>,
    <ColumnName>
)
SELECT
    <source_column_name> AS <ColumnName>,
    <source_column_name> AS <ColumnName>,
    <source_column_name> AS <ColumnName>
FROM <source_database>.<source_schema>.<source_table_name>
WHERE <optional_filter_conditions>;
```

**ETL Notes:**

- Data source(s): `<source_system_or_table_reference>`
- Refresh frequency: `<daily/weekly/monthly/on-demand>`
- Key transformation logic: `<describe any aggregations, lookups, or calculations>`

---

## 5. Change Log

| Date | Change | Author |
| --- | --- | --- |
| <YYYY-MM-DD> | Initial draft | <Author> |
