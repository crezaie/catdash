;WITH CTE AS (

	SELECT 
		--e.oepdesc AS TechName
	   E.TechName
	  ,K.[CatKPIDataID]
      ,K.[CustomerNumber]
      ,K.[ShipTo]
      ,K.[Branch]
      ,K.[Make]
      ,K.[Model]
      ,K.[SerialNumber]
      ,K.[WieseID]
      ,K.[WorkOrder]
      ,K.[WorkOrderName]
      ,K.[PromiseDate]
      ,K.[ServiceType]
      ,K.[InvoiceNumber]
      ,K.[InvoiceDate]
      ,K.[InvoiceDateTime]
      ,K.[InvoiceTotal]
      ,K.[Division]
      ,K.[SubClassShortDesc]
      ,K.[Critical]
      ,K.[MfgYear]
      ,K.[Age]
      ,K.[LastLaborDate]
      ,K.[TechAssignedDate]
      ,K.[DispatchCompleteDate]
      ,K.[DateInShop]
      ,K.[DispatchCreateDate]
      ,k.[servstart]
      ,[servstop]
      ,[MinLaborDate]
      ,[MaxLaborDate]
      ,[LaborHours]
      ,[TimeDown]
      ,[LaborDiff]
      ,[ResponseTime]
      ,[TimeToSubmit]
      ,[BHResponseTime]
      ,[BHTimeDown]
      ,[BHTimeToSubmit]
	  ,MIN(w.date1) AS MinPartOrderDate
	  ,MAX(w.date1) AS MaxPartOrderDate
	  ,wonotes

  FROM 
	  [EBSDW].[dbo].[tblCATKPIData] K
	  LEFT JOIN WieseData.dbo.WOSEGDETL W ON W.kworkorder = k.workorder and w.kbranch = '002'
	  --LEFT JOIN [WieseData].[dbo].[EMPLOY] E ON E.key_4_a1 = W.key_4_a1
	  LEFT JOIN [EBSDW].[dbo].[tblEBSWorkOrderSummary] E ON E.WorkOrder = K.WorkOrder AND E.Branch = K.Branch
  WHERE
	LTRIM(RTRIM(K.ServiceType)) NOT IN ('Logged Call','PM')
	AND K.InvoiceDate IS NOT NULL
	AND DispatchCreateDate >= '2023-03-23'

  GROUP BY
  	  [CatKPIDataID]
      ,K.[CustomerNumber]
      ,K.[ShipTo]
      ,K.[Branch]
      ,K.[Make]
      ,K.[Model]
      ,K.[SerialNumber]
      ,K.[WieseID]
      ,K.[WorkOrder]
      ,K.[WorkOrderName]
      ,K.[PromiseDate]
      ,K.[ServiceType]
      ,K.[InvoiceNumber]
      ,K.[InvoiceDate]
      ,K.[InvoiceDateTime]
      ,K.[InvoiceTotal]
      ,K.[Division]
      ,[SubClassShortDesc]
      ,[Critical]
      ,[MfgYear]
      ,[Age]
      ,[LastLaborDate]
      ,[TechAssignedDate]
      ,[DispatchCompleteDate]
      ,[DateInShop]
      ,[DispatchCreateDate]
      ,k.[servstart]
      ,[servstop]
      ,[MinLaborDate]
      ,[MaxLaborDate]
      ,[LaborHours]
      ,[TimeDown]
      ,[LaborDiff]
      ,[ResponseTime]
      ,[TimeToSubmit]
      ,[BHResponseTime]
      ,[BHTimeDown]
      ,[BHTimeToSubmit]
	  ,W.key_4_a1
	  ,E.TechName
	  ,wonotes
	  )

SELECT

	--REPLACE(REPLACE(STUFF((SELECT DISTINCT ',' + COALESCE(TechName,'SEG_NO_TECH')
 --   FROM CTE S
	--WHERE S.CATKPIDATAID = C.CATKPIDATAID
 --   FOR XML PATH('')), 1, 1, ''),',SEG_NO_TECH',''),'SEG_NO_TECH,','') AS Technician
	TechName AS Technician
	,[Branch]
	,[WorkOrder]
	,[WieseID]
	,[CustomerNumber]
	,[ShipTo]
	,[Make]
	,[Model]
	,[SerialNumber]
	,[Division]
	,[SubClassShortDesc]
	,[MfgYear]	
	
	,CATKPIDATAID
	,[WorkOrderName]
	,[PromiseDate]
	,[ServiceType]
	,[InvoiceNumber]
	,[InvoiceDate]
	,[InvoiceDateTime]
	,[InvoiceTotal]
	,[Critical]
	,[Age]
	,[LastLaborDate]
	,[TechAssignedDate]
	,[DispatchCompleteDate]
	,[DateInShop]
	,[DispatchCreateDate]
	,[servstart]
	,[servstop]
	,[MinLaborDate]
	,[MaxLaborDate]
	,[LaborHours]
	,[TimeDown]
	,[LaborDiff]
	,[ResponseTime]
	,[TimeToSubmit]
	,[BHResponseTime]
	,[BHTimeDown]
	,[BHTimeToSubmit]
	,MIN(MinPartOrderDate) AS MinPartOrderDate
	,MAX(MaxPartOrderDate) AS MaxPartOrderDate
	,STUFF((SELECT DISTINCT ',' + COALESCE(WoNotes,'SEG_NO_NOTES')
		FROM CTE W
		WHERE W.CATKPIDATAID = C.CATKPIDATAID
		FOR XML PATH('')), 1, 1, '') AS WoNotes	

INTO #FIN

FROM
	CTE C

GROUP BY 
	CATKPIDATAID
	,[CustomerNumber]
	,[ShipTo]
	,[Branch]
	,[Make]
	,[Model]
	,[SerialNumber]
	,[WieseID]
	,[WorkOrder]
	,[WorkOrderName]
	,[PromiseDate]
	,[ServiceType]
	,[InvoiceNumber]
	,[InvoiceDate]
	,[InvoiceDateTime]
	,[InvoiceTotal]
	,[Division]
	,[SubClassShortDesc]
	,[Critical]
	,[MfgYear]
	,[Age]
	,[LastLaborDate]
	,[TechAssignedDate]
	,[DispatchCompleteDate]
	,[DateInShop]
	,[DispatchCreateDate]
	,[servstart]
	,[servstop]
	,[MinLaborDate]
	,[MaxLaborDate]
	,[LaborHours]
	,[TimeDown]
	,[LaborDiff]
	,[ResponseTime]
	,[TimeToSubmit]
	,[BHResponseTime]
	,[BHTimeDown]
	,[BHTimeToSubmit]
	,TechName







------------------------BEGIN: PERFORMANCE ISSUES-----
SELECT 'Performance Issue' AS Issue, 'BHTimeDown > 16' AS IssueDesc, F.*
INTO #AGG
FROM #FIN F
WHERE
  BHTimeDown > 16

UNION
SELECT 'Performance Issue', 'BHTImeToSubmit > 16', F.*
FROM #FIN F
WHERE
  BHTImeToSubmit > 16

UNION
SELECT 'Performance Issue', 'BHResponseTime > 8', F.*
FROM #FIN F
WHERE
  BHResponseTime > 8
------------------------END: PERFORMANCE ISSUES-----



------------------------BEGIN: BAD WORKFLOW-----
UNION
SELECT 'Bad Workflow', 'PartOrderDate before MinLaborDate', F.*
FROM #FIN F
WHERE
  MinPartOrderDate < CONVERT(VARCHAR(10), MinLaborDate, 120) --MinPartOrderDate < CAST(MinLaborDate AS DATE)

UNION
SELECT 'Bad Workflow', 'negative BHResponseTime', F.*
FROM #FIN F
WHERE
  BHResponseTime < 0

UNION
SELECT 'Bad Workflow', 'negative BHTimeDown', F.*
FROM #FIN F
WHERE
  BHTimeDown < 0

UNION
SELECT 'Bad Workflow', 'negative BHTimeToSubmit', F.*
FROM #FIN F
WHERE
  BHTimeToSubmit < 0

UNION
SELECT 'Bad Workflow', 'TechAssignedDate missing',F.*
FROM #FIN F
WHERE
  COALESCE(techassigneddate,'') = ''

UNION
SELECT 'Bad Workflow', 'DispatchCreateDate missing', F.*
FROM #FIN F
WHERE
  COALESCE(dispatchcreatedate,'') = ''

UNION
SELECT 'Bad Workflow', 'No Tech Assigned to any Segment', F.*
FROM #FIN F
WHERE
  Technician = 'SEG_NO_TECH'

-------------------------END: BAD WORKFLOW-----



------------------------BEGIN: MISSING ATTRIBUTES-----
UNION
SELECT 'Missing Attributes', 'SubClassShortDesc', F.*
FROM #FIN F
WHERE
  COALESCE(SubClassShortDesc,'') = ''

UNION
SELECT 'Missing Attributes', 'MfgYear', F.*
FROM #FIN F
WHERE
  COALESCE(MfgYear,'') = ''

UNION
SELECT 'Missing Attributes', 'Division', F.*
FROM #FIN F
WHERE
  COALESCE(Division,'') = ''

UNION
SELECT 'Missing Attributes', 'ServiceType', F.*
FROM #FIN F
WHERE
  COALESCE(ServiceType,'') = ''
------------------------END: MISSING ATTRIBUTES-----





------------------------BEGIN: MISCLASSIFICATION-----
UNION
SELECT 'Misclassification', 'Service Type may need to change to damage', F.*
FROM #FIN F
WHERE
  (WorkOrderName LIKE '%damage%' or wonotes LIKE '%damage%') 
  and ServiceType <> 'Damage'
------------------------END: MISCLASSIFICATION-----





--SELECT *, ROW_NUMBER() OVER(PARTITION BY IssueDesc,WieseID ORDER BY WieseID) AS RN FROM #AGG WHERE Issue = 'Missing Attributes'

SELECT * FROM #AGG WHERE Issue <> 'Missing Attributes'
UNION
SELECT A.* FROM #AGG A INNER JOIN (SELECT CATKPIDATAID, ROW_NUMBER() OVER(PARTITION BY IssueDesc,WieseID ORDER BY WieseID) AS RN FROM #AGG WHERE Issue = 'Missing Attributes') X ON X.CatKPIDataID=A.CatKPIDataID WHERE Issue = 'Missing Attributes'
ORDER BY CATKPIDATAID


--SELECT Issue, COUNT(*) CntIssue FROM #AGG GROUP BY Issue ORDER BY CntIssue DESC
--SELECT IssueDesc, COUNT(*) CntDesc FROM #AGG GROUP BY IssueDesc ORDER BY CntDesc DESC



--SELECT REPLACE(REPLACE(Technician,',SEG_NO_TECH',''),'SEG_NO_TECH,',''), COUNT(*) CntTech FROM #AGG GROUP BY REPLACE(REPLACE(Technician,',SEG_NO_TECH',''),'SEG_NO_TECH,','') ORDER BY CntTech DESC
--SELECT REPLACE(REPLACE(Technician,',SEG_NO_TECH',''),'SEG_NO_TECH,',''), Issue, IssueDesc, COUNT(*) CntTechIssue FROM #AGG WHERE Issue <> 'Missing Attributes' GROUP BY REPLACE(REPLACE(Technician,',SEG_NO_TECH',''),'SEG_NO_TECH,',''),IssueDesc,Issue ORDER BY CntTechIssue DESC



--SELECT Issue, IssueDesc AS MissingAttribute, kequipnum, SerialNumber, WieseID, WorkOrder, InvoiceNumber, Division, SubClassShortDesc, Make, Model, MfgYear 
--FROM #AGG A
--LEFT JOIN [WieseData].[dbo].EQUIP E ON E.attchtono = A.WieseID
--WHERE Issue = 'Missing Attributes' ORDER BY WieseID



--DROP TABLE #AGG
--DROP TABLE #FIN


SELECT DISTINCT MAKE,Model,SubClassShortDesc, Division, MfgYear FROM (
SELECT A.* FROM #AGG A INNER JOIN (SELECT CATKPIDATAID, ROW_NUMBER() OVER(PARTITION BY IssueDesc,WieseID ORDER BY WieseID) AS RN FROM #AGG WHERE Issue = 'Missing Attributes') X ON X.CatKPIDataID=A.CatKPIDataID WHERE Issue = 'Missing Attributes'
) X