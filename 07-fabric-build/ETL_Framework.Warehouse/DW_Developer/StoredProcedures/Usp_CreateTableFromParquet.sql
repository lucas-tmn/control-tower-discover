CREATE   PROCEDURE DW_Developer.Usp_CreateTableFromParquet
    @DestinationDatabase NVARCHAR(128),
    @SchemaName NVARCHAR(128),
    @TableName NVARCHAR(128),
    @ParquetPath NVARCHAR(4000)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @FullTableName NVARCHAR(260);
    DECLARE @DateValue DATETIME;
    
    -- Validate inputs
    IF @DestinationDatabase IS NULL OR @DestinationDatabase = ''
    BEGIN
        RAISERROR('Destination database name cannot be null or empty', 16, 1);
        RETURN;
    END
    
    IF @SchemaName IS NULL OR @SchemaName = ''
    BEGIN
        RAISERROR('Schema name cannot be null or empty', 16, 1);
        RETURN;
    END
    
    IF @TableName IS NULL OR @TableName = ''
    BEGIN
        RAISERROR('Table name cannot be null or empty', 16, 1);
        RETURN;
    END
    
    IF @ParquetPath IS NULL OR @ParquetPath = ''
    BEGIN
        RAISERROR('Parquet path cannot be null or empty', 16, 1);
        RETURN;
    END
    
    -- Build three-part table name
    SET @FullTableName = QUOTENAME(@DestinationDatabase) + '.' + QUOTENAME(@SchemaName) + '.' + QUOTENAME(@TableName);

    SET @DateValue = GETDATE();
        SELECT
            @DateValue = CSTDateValue
        FROM
            DW_Developer.fn_GetDate(@DateValue);
    
    -- Build dynamic SQL
    SET @SQL = '
    USE ' + QUOTENAME(@DestinationDatabase) + ';
    
    -- Create schema if not exists
    --IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = ''' + @SchemaName + ''')
   -- BEGIN
    --    EXEC(''CREATE SCHEMA ' + QUOTENAME(@SchemaName) + ''');
    --END;

    -- truncate table if exists
    IF OBJECT_ID(''' + @FullTableName + ''', ''U'') IS NOT NULL
        TRUNCATE TABLE ' + @FullTableName + ';
    
    -- Create table from Parquet file
    INSERT INTO ' + @FullTableName + '
    SELECT * 
    FROM OPENROWSET(
        BULK ''' + @ParquetPath + ''',
        FORMAT = ''PARQUET''
    ) AS data;';
    
    BEGIN TRY
        EXEC sp_executesql @SQL;
        PRINT 'Successfully created table ' + @FullTableName + ' from Parquet file: ' + @ParquetPath;
        DECLARE @Exists INT
        SET @Exists = (SELECT COUNT(*)
                            FROM DW_Developer.TableDictionary 
                           WHERE DatabaseName= @DestinationDatabase 
                             AND SchemaName=  @SchemaName   
                             AND TableName=  @TableName )
        IF @Exists = 0
           INSERT INTO DW_Developer.TableDictionary
              ( ServerName, 
                DatabaseName,
                 SchemaName,
                 TableName,
                 ObjectType,
                 StorageType,
                 UpdateQuery
              )
             VALUES 
             (
                'EDW-Fabric',
                 @DestinationDatabase,
                 @SchemaName, 
                 @TableName,
                'Table',
                'Delta',
                '[DW_Developer].[Usp_CreateTableFromParquet]'
            )
        UPDATE  DW_Developer.TableDictionary 
           SET Modified = @DateValue
            WHERE DatabaseName= @DestinationDatabase 
              AND SchemaName=  @SchemaName   
              AND TableName=  @TableName
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error creating table from Parquet file: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END