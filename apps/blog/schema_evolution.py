
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
sqlite3_evolutions = [
    [('fv1:-1315803874','fv1:2038920609'), # generated 2008-04-07 07:43:05.984000
        "-- FYI: sqlite does not support adding primary keys or unique or not null fields",
        "-- FYI: so we create a new \"blog_post\" and delete the old ",
        "-- FYI: this could take a while if you have a lot of data",
        "ALTER TABLE \"blog_post\" RENAME TO \"blog_post_1337_TMP\";",
        "CREATE TABLE \"blog_post\" (\n    \"id\" integer NOT NULL PRIMARY KEY,\n    \"author_id\" integer NOT NULL,\n    \"name\" varchar(256) NOT NULL,\n    \"slug\" varchar(256) NOT NULL,\n    \"teaser\" text NOT NULL,\n    \"text\" text NOT NULL,\n    \"render_method\" varchar(15) NOT NULL,\n    \"html\" text NOT NULL,\n    \"date\" datetime NOT NULL,\n    \"upd_date\" datetime NOT NULL,\n    \"is_draft\" bool NOT NULL,\n    \"is_featured\" bool NOT NULL,\n    \"enable_comments\" bool NOT NULL,\n    \"tags\" varchar(255) NOT NULL\n)\n;",
        "INSERT INTO \"blog_post\" SELECT \"id\",\"author_id\",\"name\",\"slug\",\"teaser\",\"text\",\"render_method\",\"html\",\"date\",'',\"is_draft\",\"is_featured\",\"enable_comments\",\"tags\" FROM \"blog_post_1337_TMP\";",
        "DROP TABLE \"blog_post_1337_TMP\";",
    ],
] # don't delete this comment! ## sqlite3_evolutions_end ##
