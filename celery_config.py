broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
Timezone = 'Asia/Kolkata'
broker_connection_retry_on_startup = True

from celery.schedules import crontab

beat_schedule = {
    'send-monthly-reports': {
        'task': 'monthly_report',  # Name of the task
        'schedule': crontab(minute='*/3'),  # Run at midnight on the first day of each month
        
},


    'send-daily-reminders': {
        'task': 'daily_professional_reminder',  # Name of the daily reminder task
        'schedule': crontab(minute='*/3'),  # Runs every day at 6 PM IST
    },


}