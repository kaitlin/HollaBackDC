"""
Life is a personal event agregation application for Byteflow. It can
grab events from any service having feed.

Usage
=====

 1. Add 'nebula' and 'life' apps to ADDITIONAL_APPS in settings_local.py
 2. Run `manage.py syncdb`
 3. Add desired life flows (url to personal activity at some service)
    via admin interface or migrate from blogroll
 4. a) Fetch feeds manually via link 'fetch all feeds' at life page (only
       viewable by logged in admin)
    b) Add job to crontab to fetch feeds periodically by executing
       `manage.py fetch_feeds life`. For example, per-user crontab (edit it
       by `crontab -e`) for fetching feeds every 30 minutes looks like:
           # each 30 min fetch life feeds
           */30 * * * * /path/to/manage.py fetch_feeds --quiet life
"""
