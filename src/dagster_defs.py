import dagster as dg
from src.fetch_stock_data import main


@dg.op
def run_pipeline_op(context: dg.OpExecutionContext):
    context.log.info("Starting stock data pipeline...")
    main()
    context.log.info("Pipeline finished.")


@dg.job
def stock_pipeline_job():
    run_pipeline_op()


daily_schedule = dg.ScheduleDefinition(
    job=stock_pipeline_job,
    cron_schedule="0 0 * * *",  # midnight UTC (about 5:30 AM IST)
    execution_timezone="Asia/Kolkata",
    name="daily_stock_schedule",
)


defs = dg.Definitions(
    jobs=[stock_pipeline_job],
    schedules=[daily_schedule],
)
