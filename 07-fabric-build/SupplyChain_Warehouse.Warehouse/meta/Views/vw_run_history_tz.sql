-- Auto Generated (Do not modify) F455BE0D03715C63CE54E7773E596FA6B144947E2CB47C97B33DF7C2F8874511

CREATE   VIEW meta.vw_run_history_tz AS
SELECT
    run_id, pipeline_run_id, sp_name, status, rows_affected,
    load_type, duration_seconds, error_message,
    -- UTC (source of truth)
    start_time          AS start_utc,
    end_time            AS end_utc,
    -- CST (Enterprise/US team)
    start_cst,
    end_cst,
    -- VN (UTC+7)
    DATEADD(HOUR, 7, start_time) AS start_vn,
    DATEADD(HOUR, 7, end_time)   AS end_vn
FROM meta.sp_run_history