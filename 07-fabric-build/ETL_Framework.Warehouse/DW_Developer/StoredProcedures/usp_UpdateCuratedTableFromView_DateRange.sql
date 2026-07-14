CREATE PROC [DW_Developer].[usp_UpdateCuratedTableFromView_DateRange]
    @DestinationDatabase    VARCHAR(150),
    @DestinationSchema      VARCHAR(150),
    @DestinationTable       VARCHAR(150),
    @SourceDateColumn       VARCHAR(100),
    @DestinationDateColumn  VARCHAR(100),
    @NumberofDays           INT
    
AS

/* Change Control -----------------------------------------------------------------------------------------------------------
* Bob Horton,  A generic procedure for curating fact, dim tables using a view for the select logic 
*              the procedure keys off the date column passed in
* Bob Horton,  11/20/2023  converted to Fabric
---------------------------------------------------------------------------------------------------------------------------*/


  DECLARE
        @String    VARCHAR(5000),
        @DateValue DATETIME,
        @User      VARCHAR(500)
      
        SELECT @String
            = 'usp_UpdateCuratedTableFromView_DateRange: ' + @DestinationDatabase + '.' + @DestinationSchema + '.' + @DestinationTable;
        SELECT @User = SYSTEM_USER;
        SELECT @DateValue = GETDATE();
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

DECLARE 
    @SQLCommand		   VARCHAR(MAX),
	@RenameString      VARCHAR(750),
	@LiveTable         VARCHAR(500),
	@ViewName          VARCHAR(500),
    @MinDate           VARCHAR(20)

SELECT @MinDate = CAST(DATEADD(DAY,@NumberofDays,CAST(GETDATE() AS DATE)) AS VARCHAR(12))
SELECT @ViewName =  @DestinationDatabase + '.' + @DestinationSchema + '_Wrk.v_' + @DestinationTable
SELECT @LiveTable = @DestinationDatabase +'.' + @DestinationSchema + '.' + @DestinationTable



SELECT @SQLCommand=
     
  'DELETE FROM ' + @LiveTable + ' WHERE '+ @DestinationDateColumn + ' >= '''+ @MinDate + ''' 
   INSERT INTO ' + @LiveTable + ' SELECT * FROM ' + @ViewName +' WHERE '+ @SourceDateColumn +' >= '''+ @MinDate +''''


  SELECT @SQLCommand
  EXECUTE (@SQLCommand)

      

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
                '[DW_Developer].[usp_UpdateCuratedTableFromView_DateRange]'
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
            )

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