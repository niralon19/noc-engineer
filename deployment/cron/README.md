# Scheduled jobs

The six schedules below match the architecture design. They are job specifications; the scheduler adapter must be connected to the installed Hermes Cron facility or an approved external scheduler. Do not run both schedulers for the same job. Set timezone explicitly for the deployment; cron expressions alone do not encode timezone.
