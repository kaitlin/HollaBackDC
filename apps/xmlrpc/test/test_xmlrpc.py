from xmlrpclib import ServerProxy
server = ServerProxy("http://127.0.0.1:8000/xmlrpc/")

USERNAME = 'alberto'
PASSWORD = 'al0069'
BLOGID = 'myblog'
#    * blogger_deletePost
#    * blogger_getUsersBlogs
#blogger_getUsersBlogs(appkey, username, password)
print 'blogger_getUsersBlogs', server.blogger_getUsersBlogs('key', USERNAME, PASSWORD)

#    * metaWeblog_editPost

#    * metaWeblog_getCategories
#metaWeblog_getCategories(postid, username, password)
print 'metaWeblog_getCategories', server.metaWeblog_getCategories(1, USERNAME, PASSWORD)

#    * metaWeblog_getPost
#metaWeblog_getPost(postid, username, password))
print 'metaWeblog_getPost', server.metaWeblog_getPost(1, USERNAME, PASSWORD)

#    * metaWeblog_getRecentPosts
#metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts)
print 'metaWeblog_getRecentPosts', server.metaWeblog_getRecentPosts(BLOGID, USERNAME, PASSWORD, 10)

#    * metaWeblog_newMediaObject
#    * metaWeblog_newPost

#    * mt_getPostCategories
#mt_getPostCategories(postid, username, password)
print 'mt_getPostCategories', server.mt_getPostCategories(1, USERNAME, PASSWORD)

#    * mt_getRecentPostTitles
#mt_getRecentPostTitles(blogid, username, password, numberOfPosts)
print 'mt_getRecentPostTitles', server.mt_getRecentPostTitles(BLOGID, USERNAME, PASSWORD, 10)


#    * mt_getTrackbackPings
#    * mt_publishPost
#    * mt_setPostCategories
#    * mt_supportedMethods
#    * mt_supportedTextFilters
#    * system.listMethods
#    * system.methodHelp
#    * system.methodSignature
#    * system.multicall


#print server.blogger_getUsersBlogs('alberto','al0069', 1)
#print server.metaWeblog_getCategories('alberto','al0069', 1)
#print server.metaWeblog_getPost('alberto','al0069', 1)

#    * mt_getCategoryList
#mt_getCategoryList(blogid, username, password)
print 'mt_getCategoryList', server.mt_getCategoryList(BLOGID, USERNAME, PASSWORD)
