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