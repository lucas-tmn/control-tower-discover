CREATE PROCEDURE DW_Developer.usp_DropWorkTable @LoadTable VARCHAR(400) as
--  Created by Bob Horton 5/13/2021 
-- purpose to to have a generic process to drop work tables.   Visual Studio projects are throwing reference errors 
-- we try to drop tables inside of procedures before they get created and it is the best practice to see if they exist
-- and dropping them if they do before we create them for the current process

DECLARE @str VARCHAR(1000)

SET  @str  = 
'IF OBJECT_ID(N'''+@LoadTable+''', N''U'') IS NOT NULL 
	DROP TABLE '+@LoadTable
EXEC (@str)