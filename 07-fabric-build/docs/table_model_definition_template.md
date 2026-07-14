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

## 3. Semantic Model Layer

- **Model Type** - <e.g. Star schema, Direct Lake Query>
- **Fact Table** - <TableName>

---

### Relationships

| From | To | Type | Direction |
| --- | --- | --- | --- |
| `<TableName>[<Column>]` | `<DimTable>[<Column>]` | Many-to-One | Single |

---

## 4. Measures (DAX)

### `displayFolder: <Folder Name>`

#### <Measure Name>

```DAX
<Measure Name> = <DAX expression>
```

#### <Measure Name>

```tmdl
	measure '<Measure Name>' = <DAX expression>
		formatString: "<Format String>"
		displayFolder: "<Folder Name>"
        description: "<Measure Description>"
```

---

## 5. Source Data & ETL Logic (Optional)

```tsql
-- Load fact/dimension from source table(s)
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

## 6. Change Log

| Date | Change | Author |
| --- | --- | --- |
| `<YYYY-MM-DD>` | Initial draft | `<Author>` |
