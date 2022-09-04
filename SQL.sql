USE F1DashStreamline

DROP PROCEDURE IF EXISTS dbo._Tracing_LapSamples
GO
CREATE PROCEDURE dbo._Tracing_LapSamples @SessionDate DATE, @SessionName VARCHAR(MAX), @DriverNumber INT, @LapNumber INT
AS
BEGIN

	/*
		Query to get one lap of position samples
	*/

	DECLARE @SessionId INT
		,@LapStartTime FLOAT
		,@LapEndTime FLOAT


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


	-- Get samples

	SELECT Driver
		,[Time]
		,X
		,Y
		,Z

	FROM dbo.PositionData

	WHERE SessionId = @SessionId
	AND Driver = @DriverNumber
	AND [Time] >= @LapStartTime
	AND [Time] <= @LapEndTime

END
GO