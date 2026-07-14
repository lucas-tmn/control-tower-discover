CREATE PROCEDURE [DW_Developer].[usp_UpdateTableDictionary_ModifiedDate]
    @DestinationDatabase VARCHAR(150),
    @DestinationSchema VARCHAR(150),
    @DestinationTable VARCHAR(150),
    @UpdateQuery VARCHAR(5000) = NULL,
    @DateValue DATETIME = NULL
AS

/* Change Control -----------------------------------------------------------------------------------------------------------
* Sriraghav Venkata, A generic procedure for updating last modified date and log the update into ETL_Framework.[DW_Developer].[TableDictionary_UpdateLog]
---------------------------------------------------------------------------------------------------------------------------*/

BEGIN
    SET NOCOUNT ON;
    
    DECLARE
        @String    VARCHAR(5000),
        @User      VARCHAR(500);
        
    SET @String = 'DW_Developer.usp_UpdateTableDictionary_ModifiedDate: ' + @DestinationDatabase + '.' + @DestinationSchema + '.' + @DestinationTable;
    SET @User = SYSTEM_USER;
    
    BEGIN TRY
        -- Set default date if not provided
        IF @DateValue IS NULL
            SET @DateValue = GETDATE();
            
        SELECT @DateValue = CSTDateValue 
        FROM DW_Developer.fn_GetDate(@DateValue);
        
        -- Set default UpdateQuery if not provided
        IF @UpdateQuery IS NULL
            SET @UpdateQuery = '';

        INSERT INTO DW_Developer.AuditLog
        VALUES (@String, @DateValue, @User, 'Process Start');

        DECLARE @Exists INT;
        
        -- Check if record exists
        SET @Exists = (
            SELECT COUNT(*)
            FROM DW_Developer.TableDictionary
            WHERE DatabaseName = @DestinationDatabase 
            AND SchemaName = @DestinationSchema   
            AND TableName = @DestinationTable
        );

        -- Insert if doesn't exist
        IF @Exists = 0 
        BEGIN
            INSERT INTO DW_Developer.TableDictionary
            ( 
                ServerName, 
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
                @DestinationSchema, 
                @DestinationTable,
                'Table',
                'Delta',
                @UpdateQuery
            );
        END

        -- Update modified date
        UPDATE DW_Developer.TableDictionary
        SET Modified = @DateValue
        WHERE DatabaseName = @DestinationDatabase 
        AND SchemaName = @DestinationSchema   
        AND TableName = @DestinationTable;

        -- Log the update
        INSERT INTO DW_Developer.TableDictionary_UpdateLog
        VALUES
        (
            @DestinationDatabase, 
            @DestinationSchema,
            @DestinationTable, 
            @DateValue
        );

        INSERT INTO DW_Developer.AuditLog
        VALUES (@String, @DateValue, @User, 'Process Complete');

    END TRY
    BEGIN CATCH
        DECLARE
            @ErrorMessage  VARCHAR(4000),
            @ErrorSeverity INT,
            @ErrorState    INT;
        SET @ErrorMessage = ERROR_MESSAGE();
        SET @ErrorSeverity = ISNULL(ERROR_SEVERITY(), 16);
        SET @ErrorState = ISNULL(ERROR_STATE(), 0);
        
        SET @DateValue = GETDATE();
        SELECT @DateValue = CSTDateValue 
        FROM DW_Developer.fn_GetDate(@DateValue);

        INSERT INTO DW_Developer.AuditLog
        VALUES (@String, @DateValue, @User, @ErrorMessage);
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END