--ANYTHING RELATED TO HOUR METERS
;WITH HCTE0 AS (
	SELECT 
		MAX(K.WorkOrder) AS WorkOrder
		,Kequipnum
		,MAX(COALESCE(MeterReading,0)) MeterReading
		,CAST(DispatchCreateDate AS DATE) AS DispatchCreateDate
		,MAX(K.InvoiceDate) AS InvoiceDate
	FROM 
		[EBSDW].[dbo].[tblCATKPIData] K
		LEFT JOIN [EBSDW].[dbo].[tblEBSWorkOrderSummary] E ON E.WorkOrder = K.WorkOrder AND E.Branch = K.Branch
		LEFT JOIN [WieseData].[dbo].WOHEAD W ON W.kworkorder = K.WorkOrder AND W.kbranch = K.Branch

	GROUP BY

		Kequipnum
		,CAST(DispatchCreateDate AS DATE)		
)

,HCTE AS (
	SELECT DISTINCT
		WorkOrder
		,Kequipnum
		,MeterReading
		,row_number () OVER ( PARTITION BY kequipnum ORDER BY DispatchCreateDate) AS rn
		,DispatchCreateDate
		,InvoiceDate
	FROM 
		HCTE0
)

,HCTE2 AS (

	SELECT
		C.Kequipnum
		,C.InvoiceDate
		,C.WorkOrder AS CurrentWorkOrder, C.DispatchCreateDate AS CurrentDispatchCreateDate, COALESCE(C.MeterReading,0) AS CurrentMeterReading
		,rt.WorkOrder AS PriorWorkOrder, rt.DispatchCreateDate AS PriorDispatchCreateDate, COALESCE(rt.MeterReading,0) AS PriorMeterReading
		,DATEDIFF(DAY, rt.DispatchCreateDate, C.DispatchCreateDate) AS DaysDiff
		,DATEDIFF(DAY, rt.DispatchCreateDate, C.DispatchCreateDate)*24 AS HoursDiff
		,(COALESCE(C.MeterReading,0) - COALESCE(rt.MeterReading,0)) AS MeterReadingDiff
		
	FROM 
		HCTE C
		INNER JOIN (SELECT Kequipnum, MAX(rn) AS maxrn, MAX(rn)-1 AS rtjoin FROM HCTE GROUP BY Kequipnum) AS mx ON mx.Kequipnum = C.kequipnum AND mx.maxrn = C.rn
		LEFT JOIN HCTE rt ON rt.kequipnum = C.kequipnum AND rt.rn = mx.rtjoin

)

SELECT 
	CASE
		WHEN CurrentMeterReading = 0 THEN 'Current Hour Reading Not Submitted'
		WHEN PriorMeterReading = 0 THEN 'Prior Hour Reading Not Submitted'
		WHEN PriorMeterReading > CurrentMeterReading THEN 'Prior Reading is Greater than Current Reading'
		WHEN HoursDiff < MeterReadingDiff THEN 'Mathematically Impossible Hour Reading'
		WHEN COALESCE(MeterReadingDiff,0) = 0 THEN 'Machine Logged 0 Hours Since Last Reading'
		END AS 'MeterIssue'
	,C.* 

INTO #HRS
FROM 
	HCTE2 C

WHERE 
	(PriorWorkOrder IS NOT NULL AND (COALESCE(MeterReadingDiff,0) <= 0 OR COALESCE(HoursDiff,0) < COALESCE(MeterReadingDiff,0)))
	OR COALESCE(CurrentMeterReading,0) = 0


	
	SELECT 
		COALESCE(e.oepdesc,'SEG_NO_TECH') AS TechName
		,[WorkOrder]
	INTO #TC
	FROM 
		[EBSDW].[dbo].[tblCATKPIData] K
		INNER JOIN #HRS H ON H.CurrentWorkOrder = K.WorkOrder
		LEFT JOIN WieseData.dbo.WOSEGDETL W ON W.kworkorder = k.workorder and w.kbranch = '002'
		LEFT JOIN [WieseData].[dbo].[EMPLOY] E ON E.key_4_a1 = W.key_4_a1

	WHERE
		DispatchCreateDate >= '2023-03-23'


	SELECT
		COALESCE(REPLACE(REPLACE(STUFF((SELECT DISTINCT ',' + COALESCE(TechName,'SEG_NO_TECH')
		FROM #TC S
		WHERE S.WorkOrder = H.CurrentWorkOrder
		FOR XML PATH('')), 1, 1, ''),',SEG_NO_TECH',''),'SEG_NO_TECH,',''),'SEG_NO_TECH') AS Technician		
		,H.*
	INTO #REP

	FROM
		#HRS H
	WHERE
		MeterIssue <> 'Prior Hour Reading Not Submitted'


	--prior reading

	SELECT
		COALESCE(REPLACE(REPLACE(STUFF((SELECT DISTINCT ',' + COALESCE(TechName,'SEG_NO_TECH')
		FROM #TC S
		WHERE S.WorkOrder = H.PriorWorkOrder
		FOR XML PATH('')), 1, 1, ''),',SEG_NO_TECH',''),'SEG_NO_TECH,',''),'SEG_NO_TECH') AS Technician		
		,H.*
	INTO #REP2

	FROM
		#HRS H
	WHERE
		MeterIssue = 'Prior Hour Reading Not Submitted'

	SELECT
		Technician, MeterIssue, COUNT(*) AS IssueCount

	FROM #REP
	GROUP BY Technician, MeterIssue
	UNION
	SELECT
		Technician, MeterIssue, COUNT(*)

	FROM #REP2
	GROUP BY Technician, MeterIssue
	ORDER BY COUNT(*) DESC

SELECT * FROM #REP WHERE InvoiceDate IS NULL
UNION SELECT * FROM #REP2 WHERE InvoiceDate IS NULL
ORDER BY MeterIssue

DROP TABLE #HRS
DROP TABLE #REP
DROP TABLE #REP2
DROP TABLE #TC