CREATE PROC [DW_Developer].[usp_RefreshCuratedTableFromView]
    @DestinationDatabase VARCHAR(150),
    @DestinationSchema   VARCHAR(150),
    @DestinationTable    VARCHAR(150),
    @CheckforEmpty       INT = 0
AS

/* Change Control -----------------------------------------------------------------------------------------------------------
* Bob Horton,  A generic procedure for curating fact, dim tables using a view for the select logic
* Bob Horton,  11/09/2023  converted to Fabric
---------------------------------------------------------------------------------------------------------------------------*/


  DECLARE
            @String    VARCHAR(5000),
            @DateValue DATETIME,
            @User      VARCHAR(500);

      
        SET @String
            = 'usp_RefreshCuratedTableFromView: ' + @DestinationDatabase + '.' + @DestinationSchema + '.' + @DestinationTable;
        SET @User = SYSTEM_USER;
        SET @DateValue = GETDATE();
        SELECT
            @DateValue = CSTDateValue
        FROM
            DW_Developer.fn_GetDate(@DateValue);

        INSERT INTO DW_Developer.AuditLog
        VALUES
            (
                @String, @DateValue, @User, 'Process Start'
            );

        BEGIN TRY

            --- Initialize variables

DECLARE @SQLCommand		   VARCHAR(MAX),
		@RenameString      VARCHAR(750),
		@LiveTable         VARCHAR(500),
		@WorkTable         VARCHAR(500),
		@ViewName          VARCHAR(500)

SET @WorkTable = @DestinationDatabase +'.' + @DestinationSchema + '.' + @DestinationTable + '_LOAD'
SET @ViewName =  @DestinationDatabase + '.' + @DestinationSchema + '_Wrk.v_' + @DestinationTable
SET @LiveTable = @DestinationDatabase +'.' + @DestinationSchema + '.' + @DestinationTable

EXECUTE DW_Developer.usp_DropWorkTable  @WorkTable;

--- Create the work table from the work veiw,  if zero rows in view, skip the insert command to avoid truncate errors

SELECT @SQLCommand=
'    USE '+@DestinationDatabase+ ' 
      
            DECLARE
                @CreateTableString VARCHAR(MAX)
            SET @CreateTableString=''DECLARE  @RowCount BIGINT '


            IF @CheckforEmpty = 1 
              BEGIN
                SELECT @SQLCommand=@SQLCommand+' SET @RowCount = (SELECT COUNT(*) FROM '+@ViewName+ ') '
              END
            ELSE
               BEGIN
                 SELECT @SQLCommand=@SQLCommand+' SET @RowCount = 1 '
               END

           SELECT @SQLCommand=@SQLCommand+'
   
            CREATE TABLE ' + @WorkTable + '  AS SELECT TOP 0 *  FROM ' + @LiveTable + ' 
                          
            IF @RowCount > 0 
             BEGIN    
                                      INSERT INTO ' + @WorkTable + ' SELECT * FROM ' + @ViewName +' 
             END ''                       

            SELECT @CreateTableString;
            EXECUTE (@CreateTableString);


  
'

SELECT @SQLCommand
EXECUTE (@SQLCommand)
            ---- Drop live Table, Rename work table to take it''s place

            EXEC DW_Developer.usp_DropWorkTable  @LiveTable;

            SET @RenameString = 'USE '+@DestinationDatabase+'
			 EXEC sp_rename @objname = ''' + @WorkTable + ''', @newname = ''' + @DestinationTable + ''', @objtype = ''OBJECT'''
			
			--SELECT @RenameString
			EXECUTE (@RenameString);


SET @DateValue = GETDATE();
        SELECT
            @DateValue = CSTDateValue
        FROM
            DW_Developer.fn_GetDate(@DateValue);

        INSERT INTO DW_Developer.AuditLog
        VALUES
            (
                @String, @DateValue, @User, 'Process Complete'
            );


        --- Update last modified in Table Dictionary 
        DECLARE @Exists INT
        SET @Exists = (SELECT COUNT(*)
                            FROM DW_Developer.TableDictionary 
                           WHERE DatabaseName= @DestinationDatabase 
                             AND SchemaName=  @DestinationSchema   
                             AND TableName=  @DestinationTable )

        IF @Exists = 0 
          BEGIN

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
                 @DestinationSchema, 
                 @DestinationTable,
                'Table',
                'Delta',
                '[DW_Developer].[usp_RefreshCuratedTableFromView]'
            )

          END

        UPDATE  DW_Developer.TableDictionary 
           SET Modified = @DateValue
            WHERE DatabaseName= @DestinationDatabase 
              AND SchemaName=  @DestinationSchema   
              AND TableName=  @DestinationTable                       


        INSERT INTO DW_Developer.TableDictionary_UpdateLog
        VALUES
            (
                @DestinationDatabase, 
                @DestinationSchema,
                @DestinationTable, 
                @DateValue
            );


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
            SELECT
                @DateValue = CSTDateValue
            FROM
                DW_Developer.fn_GetDate(@DateValue);

            INSERT INTO DW_Developer.AuditLog
            VALUES
                (
                    @String, @DateValue, @User, @ErrorMessage
                );

            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);

        END CATCH;