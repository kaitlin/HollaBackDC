"""
Friends is a blogroll (actually "feedroll") application for Byteflow,
intended to aggregate all feed in planet-like style.

Usage
=====

 1. Add 'nebula' and 'friends' apps to ADDITIONAL_APPS in settings_local.py
 2. Run `manage.py syncdb`
 3. Add desired blogs via admin interface or migrate from blogroll
 4. a) Fetch feeds manually via link 'fetch all feeds' at friends page (only
       viewable by logged in admin)
    b) Add job to crontab to fetch feeds periodically by executing
       `manage.py fetch_feeds friends`. For example, per-user crontab (edit it
       by `crontab -e`) for fetching feeds every 3 hours looks like:
           # each three hours  fetch friends feeds
           00 */3 * * * /path/to/manage.py fetch_feeds --quiet friends
"""
