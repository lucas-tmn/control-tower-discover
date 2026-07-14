CREATE PROC [DW_Developer].[usp_DropConstraints]
    (@DatabaseName VARCHAR(200))
AS

   --ETL_Framework.[DW_Developer].[usp_DropConstraints] 'Finance_Warehouse'
   -- Drops all unque key and primary key constraints blocking drop/rename refresh logic... constraints likely created by data modeling (PowerBI retains the relationsihps in the model without the constraints existing)

    DECLARE @SQLCommand VARCHAR(MAX);
    SET @SQLCommand
        = 'USE ' + @DatabaseName
          + ' 
    DECLARE
	
        @TableName      VARCHAR(200),
		@SchemaName     VARCHAR(200),
        @ConstraintName VARCHAR(200),
        @ConstraintType VARCHAR(10),
        @ColumnName     VARCHAR(100),
        @ObjectType     CHAR(1),
        @Counter        INT,
        @CounterMax     INT,
        @DropSQL        VARCHAR(6000),
		@SQLInsert      VARCHAR(8000)
			   
    CREATE TABLE #Constraints
        (
            rowID          INT,
            TableName      VARCHAR(200),
			SchemaName     VARCHAR(200),
            ConstraintName VARCHAR(200),
            ConstraintType VARCHAR(20),
            ColumnName     VARCHAR(200),
            ObjectType     CHAR(1)
        )


     INSERT INTO #Constraints
  
        (
            rowID,
            TableName,
			SchemaName,
            ConstraintName,
            ConstraintType,
            ColumnName,
            ObjectType
        )
                SELECT DISTINCT
                       ROW_NUMBER() OVER (ORDER BY
                                           ConstraintName
                                         ),
                       TableName,
					   SchemaName,
                       ConstraintName,
                       ConstraintType,
                       ColumnName,
                       ObjectType
                FROM
                       (
                           SELECT
                                   tables.name               AS TableName,
                                   schemas.name              AS SchemaName,
                                   key_constraints.name      AS ConstraintName,
                                   key_constraints.type_desc AS ConstraintType,
                                   columns.name              AS ColumnName,
                                   ''T''                       AS ObjectType
                           FROM
                                   sys.tables
                               INNER JOIN
                                   sys.schemas
                                       ON tables.schema_id = schemas.schema_id
                               INNER JOIN
                                   sys.indexes
                                       ON tables.object_id = indexes.object_id
                               INNER JOIN
                                   sys.index_columns
                                       ON indexes.object_id = index_columns.object_id
                                          AND indexes.index_id = index_columns.index_id
                               INNER JOIN
                                   sys.columns
                                       ON index_columns.object_id = columns.object_id
                                          AND index_columns.column_id = columns.column_id
                               INNER JOIN
                                   sys.key_constraints
                                       ON indexes.object_id = key_constraints.parent_object_id
                                          AND indexes.name = key_constraints.name
                           WHERE
                                   key_constraints.type IN (
                                                               ''PK'', ''UQ'', ''F''
                                                           )
                           UNION
                           SELECT
                                   views.name                AS TableName,
                                   schemas.name              AS SchemaName,
                                   key_constraints.name      AS ConstraintName,
                                   key_constraints.type_desc AS ConstraintType,
                                   columns.name              AS ColumnName,
                                   ''V''                       AS ObjectType
                           FROM
                                   sys.views
                               INNER JOIN
                                   sys.schemas
                                       ON views.schema_id = schemas.schema_id
                               INNER JOIN
                                   sys.indexes
                                       ON views.object_id = indexes.object_id
                               INNER JOIN
                                   sys.index_columns
                                       ON indexes.object_id = index_columns.object_id
                                          AND indexes.index_id = index_columns.index_id
                               INNER JOIN
                                   sys.columns
                                       ON index_columns.object_id = columns.object_id
                                          AND index_columns.column_id = columns.column_id
                               INNER JOIN
                                   sys.key_constraints
                                       ON indexes.object_id = key_constraints.parent_object_id
                                          AND indexes.name = key_constraints.name
                           WHERE
                                   key_constraints.type IN (
                                                               ''PK'', ''UQ'', ''F''
                                                           )
                           UNION
                           SELECT
                                   tables.name       AS TableName,
                                   schemas.name      AS SchemaName,
                                   foreign_keys.name AS ConstraintName,
                                   ''FOREIGN KEY''     AS ConstraintType,
                                   columns.name      AS ColumnName,
                                   ''T''               AS ObjectType
                           FROM
                                   sys.tables
                               INNER JOIN
                                   sys.schemas
                                       ON tables.schema_id = schemas.schema_id
                               INNER JOIN
                                   sys.foreign_keys
                                       ON tables.object_id = foreign_keys.parent_object_id
                               INNER JOIN
                                   sys.foreign_key_columns
                                       ON foreign_keys.object_id = foreign_key_columns.constraint_object_id
                               INNER JOIN
                                   sys.columns
                                       ON foreign_key_columns.parent_object_id = columns.object_id
                                          AND foreign_key_columns.parent_column_id = columns.column_id
                           UNION
                           SELECT
                                   views.name        AS TableName,
                                   schemas.name      AS SchemaName,
                                   foreign_keys.name AS ConstraintName,
                                   ''FOREIGN KEY''     AS ConstraintType,
                                   columns.name      AS ColumnName,
                                   ''V''               AS ObjectType
                           FROM
                                   sys.views
                               INNER JOIN
                                   sys.schemas
                                       ON views.schema_id = schemas.schema_id
                               INNER JOIN
                                   sys.foreign_keys
                                       ON views.object_id = foreign_keys.parent_object_id
                               INNER JOIN
                                   sys.foreign_key_columns
                                       ON foreign_keys.object_id = foreign_key_columns.constraint_object_id
                               INNER JOIN
                                   sys.columns
                                       ON foreign_key_columns.parent_object_id = columns.object_id
                                          AND foreign_key_columns.parent_column_id = columns.column_id
                       ) Constraints;


select * from #Constraints

    SET @Counter = 1;
    SET @CounterMax =
        (
            SELECT
                COUNT(*)
            FROM
                #Constraints
        );

select @Counter,@CounterMax
    WHILE @Counter <= @CounterMax
        BEGIN
            PRINT @Counter;
            SET @TableName =
                (
                    SELECT
                        LTRIM(RTRIM(TableName))
                    FROM
                        #Constraints
                    WHERE
                        rowID = @Counter
                );

            SET @SchemaName =
                (
                    SELECT
                        LTRIM(RTRIM(SchemaName))
                    FROM
                        #Constraints
                    WHERE
                        rowID = @Counter
                );
 
            SET @ConstraintName =
                (
                    SELECT
                        LTRIM(RTRIM(ConstraintName))
                    FROM
                        #Constraints
                    WHERE
                        rowID = @Counter
                );

            SET @ObjectType =
                (
                    SELECT
                        LTRIM(RTRIM(ObjectType))
                    FROM
                        #Constraints
                    WHERE
                        rowID = @Counter
                );

         PRINT @TableName + ''.'' + @ConstraintName;

         SET @DropSQL
             = ''alter table '' + @SchemaName + ''.'' + @TableName + '' drop constraint '' + @ConstraintName;
 
            PRINT @DropSQL;

            EXEC (@DropSQL);

            SET @Counter = @Counter + 1;
        END;



    DROP TABLE #Constraints;
'   ;
    EXEC (@SQLCommand);