#!/bin/lua
-- LUA-Based Directory Watcher                                                                                                                                  
-- inotify.so needs to go into /usr/lib64/lua/5.1/                                                                                                              
                                                                                                                                                                
local inotify = require 'inotify'                                                                                                                               
local handle = inotify.init()                                                                                                                                   
                                                                                                                                                                
local psql_command = "psql -h localhost -c 'SELECT master_initialize_node_metadata();'"                                                                                                                       
local file_to_watch = "/etc/citus/citus-nodes-data/pg_worker_list.conf"                                                                                                          
                                                                                                                                                                
local wd = handle:addwatch(file_to_watch, inotify.IN_MODIFY)                                                                                                    

for ev in handle:events() do                                                                                                                                    
        os.execute(psql_command)                                                                                                                                
end                                                                                                                                                             
                                                                                                                                                                
handle:rmwatch()                                                                                                                                                
handle:close() 

