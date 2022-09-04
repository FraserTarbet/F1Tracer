import sqlalchemy
import pandas as pd


def get_sqlalchemy_engine():

    server = "DESKTOP-O203E5C\SAMPLESERVER"
    database = "F1DashStreamline"
    engine = sqlalchemy.create_engine(
        "mssql+pyodbc://"+server+"/"+database+"?driver=ODBC+Driver+13+for+SQL+Server&trusted_connection=yes&mars_connection=yes",
        fast_executemany=True, pool_pre_ping=True, pool_recycle=3600
    )

    return engine


def read_lap_samples(session_date, session_name, driver_number, lap_number):
    sqlalchemy_engine = get_sqlalchemy_engine()
    sql_query = f"""
        SET NOCOUNT ON;

        EXEC dbo._Tracing_LapSamples 
            @SessionDate = '{session_date}',
            @SessionName = '{session_name}',
            @DriverNumber = {driver_number},
            @LapNumber = {lap_number}
    """
    frame = pd.read_sql_query(sql_query, sqlalchemy_engine)
    sqlalchemy_engine.dispose()

    return frame
