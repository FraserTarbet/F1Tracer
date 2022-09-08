USE F1DashStreamline

DROP PROCEDURE IF EXISTS dbo._Tracing_LapSamples
GO
CREATE PROCEDURE dbo._Tracing_LapSamples @SessionDate DATE, @SessionName VARCHAR(MAX), @DriverNumber INT, @LapNumber INT, @BufferSeconds INT = 0
AS
BEGIN

	/*
		Query to get one lap of position samples
	*/

	DECLARE @SessionId INT
		,@LapStartTime FLOAT
		,@LapEndTime FLOAT
		,@Tla VARCHAR(3)
		,@TeamColour VARCHAR(6)
		,@BufferTime FLOAT

	SET @BufferTime = CAST(@BufferSeconds AS FLOAT) * 1000000000


	-- Identify lap parameters
	SELECT @SessionId = S.id
		,@LapStartTime = L.TimeStart
		,@LapEndTime = L.TimeEnd

	FROM dbo.Session AS S

	INNER JOIN dbo.MergedLapData AS L
	ON S.id = L.SessionId

	WHERE CAST(S.SessionDate AS DATE) = @SessionDate
	AND S.SessionName = @SessionName
	AND L.Driver = @DriverNumber
	AND L.NumberOfLaps = @LapNumber

	-- Get driver info
	SELECT @Tla = Tla
		,@TeamColour = TeamColour

	FROM dbo.DriverInfo

	WHERE SessionId = @SessionId
	AND RacingNumber = @DriverNumber


	-- Get samples
	SELECT Driver
		,@Tla AS Tla
		,@TeamColour AS TeamColour
		,@LapStartTime AS LapStartTime
		,@LapEndTime AS LapEndTime
		,[Time]
		,X
		,Y
		,Z

	FROM dbo.PositionData

	WHERE SessionId = @SessionId
	AND Driver = @DriverNumber
	AND [Time] >= @LapStartTime - @BufferTime
	AND [Time] <= @LapEndTime + @BufferTime

END
GO


DROP PROCEDURE IF EXISTS dbo._Tracing_Times
GO
CREATE PROCEDURE dbo._Tracing_Times @SessionDate DATE, @SessionName VARCHAR(MAX), @DriverNumber INT, @LapNumber INT
AS
BEGIN

	/*
		Lap and sector times for readouts
	*/

	SELECT L.Driver
		,D.Tla
		,D.TeamColour
		,L.TimeStart AS LapStartTime
		,L.TimeEnd AS LapEndTime
		,SUM(CASE WHEN Sec.SectorNumber = 1 THEN Sec.SectorSessionTime ELSE 0 END) AS Sector1EndTime
		,SUM(CASE WHEN Sec.SectorNumber = 2 THEN Sec.SectorSessionTime ELSE 0 END) AS Sector2EndTime
		,SUM(CASE WHEN Sec.SectorNumber = 3 THEN Sec.SectorSessionTime ELSE 0 END) AS Sector3EndTime
		,L.LapTime
		,SUM(CASE WHEN Sec.SectorNumber = 1 THEN Sec.SectorTime ELSE 0 END) AS Sector1Time
		,SUM(CASE WHEN Sec.SectorNumber = 2 THEN Sec.SectorTime ELSE 0 END) AS Sector2Time
		,SUM(CASE WHEN Sec.SectorNumber = 3 THEN Sec.SectorTime ELSE 0 END) AS Sector3Time

	FROM dbo.Session AS S

	INNER JOIN dbo.MergedLapData AS L
	ON S.id = L.SessionId

	INNER JOIN dbo.Sector AS Sec
	ON L.LapId = Sec.LapId

	INNER JOIN dbo.DriverInfo AS D
	ON L.Driver = D.RacingNumber

	WHERE CAST(S.SessionDate AS DATE) = @SessionDate
	AND S.SessionName = @SessionName
	AND L.Driver = @DriverNumber
	AND L.NumberOfLaps = @LapNumber

	GROUP BY L.Driver
		,D.Tla
		,D.TeamColour
		,L.TimeStart
		,L.TimeEnd
		,L.LapTime


END
GO