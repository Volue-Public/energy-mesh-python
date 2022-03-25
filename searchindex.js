Search.setIndex({docnames:["api","authentication","examples","faq","glossary","index","installation","introduction_to_mesh","mesh_client","mesh_concepts","mesh_functions","mesh_object_attributes","mesh_search","mesh_server","mesh_session","quickstart","tests","timeseries","usecases","versions"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api.rst","authentication.rst","examples.rst","faq.rst","glossary.rst","index.rst","installation.rst","introduction_to_mesh.rst","mesh_client.rst","mesh_concepts.rst","mesh_functions.rst","mesh_object_attributes.rst","mesh_search.rst","mesh_server.rst","mesh_session.rst","quickstart.rst","tests.rst","timeseries.rst","usecases.rst","versions.rst"],objects:{"volue.mesh":[[0,1,1,"","Authentication"],[0,1,1,"","Connection"],[0,1,1,"","Credentials"],[0,1,1,"","MeshObjectId"],[0,1,1,"","Timeseries"],[0,0,0,"-","aio"],[0,0,0,"-","calc"],[0,0,0,"-","examples"],[0,0,0,"-","tests"]],"volue.mesh.Authentication":[[0,1,1,"","KerberosTokenIterator"],[0,1,1,"","Parameters"],[0,2,1,"","__init__"],[0,2,1,"","delete_access_token"],[0,2,1,"","get_token"],[0,2,1,"","is_token_valid"]],"volue.mesh.Authentication.KerberosTokenIterator":[[0,2,1,"","__init__"],[0,2,1,"","process_response"],[0,2,1,"","signal_final_response_received"]],"volue.mesh.Authentication.Parameters":[[0,3,1,"","service_principal"],[0,3,1,"","user_principal"]],"volue.mesh.Connection":[[0,1,1,"","Session"],[0,2,1,"","__init__"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.Connection.Session":[[0,2,1,"","__init__"],[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","forecast_functions"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","history_functions"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","statistical_functions"],[0,2,1,"","transform_functions"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.Credentials":[[0,2,1,"","__init__"]],"volue.mesh.MeshObjectId":[[0,3,1,"","full_name"],[0,3,1,"","timskey"],[0,3,1,"","uuid_id"],[0,2,1,"","with_full_name"],[0,2,1,"","with_timskey"],[0,2,1,"","with_uuid_id"]],"volue.mesh.Timeseries":[[0,1,1,"","Curve"],[0,1,1,"","PointFlags"],[0,1,1,"","Resolution"],[0,2,1,"","__init__"],[0,4,1,"","is_calculation_expression_result"],[0,4,1,"","number_of_points"],[0,3,1,"","schema"]],"volue.mesh.Timeseries.Curve":[[0,3,1,"","PIECEWISELINEAR"],[0,3,1,"","STAIRCASE"],[0,3,1,"","STAIRCASESTARTOFSTEP"],[0,3,1,"","UNKNOWN"]],"volue.mesh.Timeseries.PointFlags":[[0,3,1,"","MISSING"],[0,3,1,"","NOT_OK"],[0,3,1,"","OK"]],"volue.mesh.Timeseries.Resolution":[[0,3,1,"","BREAKPOINT"],[0,3,1,"","DAY"],[0,3,1,"","HOUR"],[0,3,1,"","MIN15"],[0,3,1,"","MONTH"],[0,3,1,"","UNSPECIFIED"],[0,3,1,"","WEEK"],[0,3,1,"","YEAR"]],"volue.mesh.aio":[[0,1,1,"","Connection"]],"volue.mesh.aio.Connection":[[0,1,1,"","Session"],[0,2,1,"","__init__"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.aio.Connection.Session":[[0,2,1,"","__init__"],[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","forecast_functions"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","history_functions"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","statistical_functions"],[0,2,1,"","transform_functions"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.calc":[[0,0,0,"-","common"],[0,0,0,"-","forecast"],[0,0,0,"-","history"],[0,0,0,"-","statistical"],[0,0,0,"-","transform"]],"volue.mesh.calc.common":[[0,1,1,"","Timezone"]],"volue.mesh.calc.common.Timezone":[[0,3,1,"","LOCAL"],[0,3,1,"","STANDARD"],[0,3,1,"","UTC"]],"volue.mesh.calc.forecast":[[0,1,1,"","ForecastFunctions"],[0,1,1,"","ForecastFunctionsAsync"]],"volue.mesh.calc.forecast.ForecastFunctions":[[0,2,1,"","get_all_forecasts"],[0,2,1,"","get_forecast"]],"volue.mesh.calc.forecast.ForecastFunctionsAsync":[[0,2,1,"","get_all_forecasts"],[0,2,1,"","get_forecast"]],"volue.mesh.calc.history":[[0,1,1,"","HistoryFunctions"],[0,1,1,"","HistoryFunctionsAsync"]],"volue.mesh.calc.history.HistoryFunctions":[[0,2,1,"","get_ts_as_of_time"],[0,2,1,"","get_ts_historical_versions"]],"volue.mesh.calc.history.HistoryFunctionsAsync":[[0,2,1,"","get_ts_as_of_time"],[0,2,1,"","get_ts_historical_versions"]],"volue.mesh.calc.statistical":[[0,1,1,"","StatisticalFunctions"],[0,1,1,"","StatisticalFunctionsAsync"]],"volue.mesh.calc.statistical.StatisticalFunctions":[[0,2,1,"","sum"],[0,2,1,"","sum_single_timeseries"]],"volue.mesh.calc.statistical.StatisticalFunctionsAsync":[[0,2,1,"","sum"],[0,2,1,"","sum_single_timeseries"]],"volue.mesh.calc.transform":[[0,1,1,"","Method"],[0,1,1,"","TransformFunctions"],[0,1,1,"","TransformFunctionsAsync"]],"volue.mesh.calc.transform.Method":[[0,3,1,"","AVG"],[0,3,1,"","AVGI"],[0,3,1,"","FIRST"],[0,3,1,"","LAST"],[0,3,1,"","MAX"],[0,3,1,"","MIN"],[0,3,1,"","SUM"],[0,3,1,"","SUMI"]],"volue.mesh.calc.transform.TransformFunctions":[[0,2,1,"","transform"]],"volue.mesh.calc.transform.TransformFunctionsAsync":[[0,2,1,"","transform"]],"volue.mesh.examples":[[0,0,0,"-","connect_asynchronously"],[0,0,0,"-","connect_synchronously"],[0,0,0,"-","get_version"],[0,0,0,"-","quickstart"],[0,0,0,"-","read_timeseries_points"],[0,0,0,"-","read_timeseries_points_async"],[0,0,0,"-","timeseries_operations"],[0,0,0,"-","write_timeseries_points"],[0,0,0,"-","write_timeseries_points_async"]],"volue.mesh.examples.connect_asynchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.connect_synchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.get_version":[[0,5,1,"","main"]],"volue.mesh.examples.quickstart":[[0,5,1,"","main"]],"volue.mesh.examples.read_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points"]],"volue.mesh.examples.read_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points_async"]],"volue.mesh.examples.timeseries_operations":[[0,5,1,"","main"]],"volue.mesh.examples.write_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.examples.write_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.tests":[[0,0,0,"-","test_aio_connection"],[0,0,0,"-","test_authentication"],[0,0,0,"-","test_connection"],[0,0,0,"-","test_examples"],[0,0,0,"-","test_session"],[0,0,0,"-","test_timeseries"]],"volue.mesh.tests.test_aio_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_forecast_get_all_forecasts"],[0,5,1,"","test_forecast_get_forecast"],[0,5,1,"","test_get_timeseries_async"],[0,5,1,"","test_history_get_ts_as_of_time"],[0,5,1,"","test_history_get_ts_historical_versions"],[0,5,1,"","test_read_timeseries_attribute_async"],[0,5,1,"","test_read_timeseries_points_async"],[0,5,1,"","test_read_timeseries_points_with_different_datetime_timezones_async"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute_async"],[0,5,1,"","test_statistical_sum"],[0,5,1,"","test_statistical_sum_single_timeseries"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation_async"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference_async"],[0,5,1,"","test_update_timeseries_entry_async"],[0,5,1,"","test_write_timeseries_points_async"],[0,5,1,"","test_write_timeseries_points_using_timskey_async"],[0,5,1,"","test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones_async"]],"volue.mesh.tests.test_authentication":[[0,5,1,"","auth_metadata_plugin"],[0,5,1,"","connection"],[0,5,1,"","get_async_connection"],[0,5,1,"","test_async_connection_get_user_identity"],[0,5,1,"","test_async_connection_revoke_access_token"],[0,5,1,"","test_auth_metadata_plugin_obtains_correctly_new_token_after_delete"],[0,5,1,"","test_auth_metadata_plugin_obtains_valid_token_in_init"],[0,5,1,"","test_connection_get_user_identity"],[0,5,1,"","test_connection_revoke_access_token"],[0,5,1,"","test_delete_access_token"],[0,5,1,"","test_is_valid_token_returns_false_for_deleted_access_token"]],"volue.mesh.tests.test_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_forecast_get_all_forecasts"],[0,5,1,"","test_forecast_get_forecast"],[0,5,1,"","test_get_timeseries"],[0,5,1,"","test_history_get_ts_as_of_time"],[0,5,1,"","test_history_get_ts_historical_versions"],[0,5,1,"","test_read_timeseries_attribute"],[0,5,1,"","test_read_timeseries_points"],[0,5,1,"","test_read_timeseries_points_with_different_datetime_timezones"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute"],[0,5,1,"","test_statistical_sum"],[0,5,1,"","test_statistical_sum_single_timeseries"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference"],[0,5,1,"","test_update_timeseries_entry"],[0,5,1,"","test_write_timeseries_points"],[0,5,1,"","test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones"]],"volue.mesh.tests.test_examples":[[0,5,1,"","test_is_grpc_responding"],[0,5,1,"","test_run_example_scripts"]],"volue.mesh.tests.test_session":[[0,5,1,"","test_async_get_version"],[0,5,1,"","test_can_connect_to_existing_session"],[0,5,1,"","test_get_version"],[0,5,1,"","test_open_and_close_session"],[0,5,1,"","test_sessions_using_async_contextmanager"],[0,5,1,"","test_sessions_using_contextmanager"]],"volue.mesh.tests.test_timeseries":[[0,5,1,"","test_can_create_empty_timeserie"],[0,5,1,"","test_can_create_timeserie_from_existing_data"],[0,5,1,"","test_can_serialize_and_deserialize_write_timeserie_request"]],volue:[[0,0,0,"-","mesh"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","property","Python property"],"5":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:property","5":"py:function"},terms:{"0":[0,2,5,8,10,15,16],"0000":2,"000000000000":2,"00000003":2,"0000000b":2,"0001":2,"0003":2,"01":[0,17],"09":3,"0max":[0,10],"0min":[0,10],"1":[0,1,2,5,6,8,10,14,15,16,18,19],"10":[0,2,8,10,18],"100":19,"1000":2,"100000f7":3,"101":19,"102":19,"1073741824":0,"109":19,"115":19,"116":19,"12":[2,8,16,19],"120":19,"122":19,"123e4567":[2,14],"125":19,"12d3":[2,14],"133":19,"134":19,"135":19,"138":19,"1468":3,"1970":[0,17],"2":[0,2,5,8,10,14,16],"2016":[2,8],"2021":18,"2078":[0,1,2,16],"24":[0,2,8,10],"26":3,"29912":3,"3":[0,2,5,6,8,10,14,15,16],"32":17,"3600":[0,10],"3ecf8ab0e2d4":18,"4":[0,2,8,16],"4299":18,"5":[0,2,8,10],"50051":[2,15,16,18],"55":10,"556642440000":[2,14],"59":3,"6":[0,2,10],"667000000":3,"67108864":0,"7":[0,5,6,8,10,15,19],"72":[2,8],"8":[0,2,5,6,10,15,19],"801896b0":18,"86400":[0,10],"874a":18,"9":[5,6,15,18,19],"99":15,"break":[0,10],"byte":[0,2,16],"case":[0,1,2,3,5,8,12,15,16,19],"class":[0,10],"default":[6,11,15],"do":[2,5,6,8,16,18],"enum":0,"final":[0,18],"float":[0,10,17],"function":[1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,19],"import":[1,2,7,8,14,15,16],"int":[0,2,8,10],"long":[0,8,10],"new":[0,1,2,5,6,10,12,14,18],"return":[0,2,8,10,19],"throw":0,"true":[0,2,3,8,12,18],"try":[0,2,3,5,8,14,18],"while":[8,10],A:[0,2,4,8,9,10,11,12,13,14,17],AND:12,As:[6,8],For:[0,1,3,6,9,10,12,15],If:[0,1,2,3,5,6,8,10,11,12,14,15,16],In:[0,3,8,15,16],Is:3,It:[0,1,10,12,15,17],NOT:0,No:[0,2,8],OR:[2,12],One:[9,13],Or:[1,2,6],The:[0,1,2,5,6,8,9,10,11,12,13,14,15,16,17],Then:18,There:[0,6,9],These:[2,6,9,16,18],To:[1,5,6,7,9,12,13,16,18],__init__:0,__main__:[1,2,8,14,15,16],__name__:[1,2,8,14,15,16],_authent:0,_common:[0,10],_connect:0,_get_connection_info:[1,2,8,14,15],_timeseri:[0,10],a456:[2,14],abl:[6,7,8,9,12,13,16,18],about:[0,10,14,18,19],abov:[3,10,13],accept:[0,2,8,12,19],access:[0,1,2,6,10,12,13],account:[0,1,2,16],accumul:[0,10],aconnect:[1,2],acquir:[0,17],action:[0,1,10],activ:[0,1,6,13,19],actual:0,ad:[0,1,2,6,11,13,16,19],add:[5,6],addit:[1,6,11,18],address:[0,1,2,3,6,8,13,14,15,16,18],adjust:[2,8],adus:0,affect:14,after:[0,1,6,10,14,17],aio:[1,2,5,8],aka:[8,9,11],aliv:0,all:[0,1,2,3,6,8,9,10,11,12,16,17,18],allevi:17,allow:16,along:6,alpha:5,also:[1,6],alwai:[2,8,12],am:5,among:14,an:[0,2,5,6,8,9,10,11,12,13,14,15,18],ani:[0,1,2,3,8,9,10,11,14,17],anoth:[0,9,10,17],anyon:1,apach:[5,6,8,17],api:[1,4,5,12,14],append:[2,8,18],appli:[0,12],applic:[4,13],ar:[0,1,2,3,5,6,8,9,10,11,12,14,15,16,17,18],arbitrari:6,architectur:7,area:[4,9],argument:[0,2,8,10],arrai:[0,2,8,10],arrang:9,arrow:[0,2,5,6,8,17],arrow_t:[2,8,18],ask:[5,10,15],asset:[4,9],associ:[0,17],assum:[6,15],async:[0,2,5,8,10],asyncconnect:[0,1,2],asynchron:[0,1,5,10],asyncio:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],attach:14,attribut:[0,5,8,9,12],attributenam:12,auth:0,auth_metadata_plugin:0,authent:[0,2,3,13,16,19],authenticatekerbero:[0,1],authentication_paramet:[0,1,2],author:[0,1,5,13],automat:[1,19],avail:[0,6,9,10,16],available_at_timepoint:[0,10],avg:[0,10],avgi:[0,10],avoid:14,await:[2,5,8],awar:[0,2,8,18],axi:10,b:[2,8,10],back:[2,8],base:[0,2,3,6,7,9,10,12,13],basic:[4,7],becaus:[0,1,2,8],been:[0,14,17],befor:[0,8,10],behav:[0,19],being:[0,10],believ:3,below:[0,6,8,10],besid:17,between:[0,9,12],binari:6,bit:17,board:3,bool:0,both:[0,2,10,17,19],bracket:12,breakpoint:[0,17],bring:6,buffer:8,bug:[5,19],build:[6,9],build_dat:15,built:13,c:[0,2,10,16],cach:16,calc:[2,5,8,10,12],calcul:[4,5,9,11,12,14],call:[0,1,2,5,6,8,11,13],can:[0,1,2,3,6,8,9,10,11,12,13,14,15,16,17],cancel:0,catalog:0,categori:10,caus:3,cc:3,center:1,cert:[2,16],certain:0,certif:[0,2,13,16],challeng:0,chang:[0,2,3,5,6,8,10,14,15,16],channel:0,channel_credenti:0,channelcredenti:0,charact:[0,1,2,10,12,16],check:[0,2,3,8,14,15],child:12,children:2,chimney2timeseriesraw:2,classmethod:0,clean:0,click:6,client:[0,1,2,3,5,7,8,10,13],clone:6,close:[0,2,8,13,14,15],closest:12,cloud:6,cmd:[2,16],coarser:[0,10],code:[0,2,3,6,15],collect:[4,9,12],com:[0,1,2,6,15,16,19],combin:[0,10,11],come:[6,9,10],command:[6,18],commit:[0,2,14,15,19],common:[0,2,8,10,17],commun:[0,1,2,5,6,8,13,15,18,19],compani:[1,2,16],companyad:[1,2,16],comparison:12,compat:5,complet:0,composit:12,compound_stmt:0,comput:13,concept:[0,4,6,7,8],concurr:[0,2,8],confidenti:3,config:6,configur:[0,1,2,5,6,10,13,14,15],confirm:1,connect:[0,1,5,8,9,10,11,13,14,15,16,18,19],connect_asynchron:0,connect_synchron:0,connect_to_sess:[0,2,14],consid:[0,10],consist:[0,1,7,11,12,17],consolid:4,consult:[1,3,15],consum:17,contact:[1,3,15],contain:[0,2,9,10,18],context:0,contextmanag:0,contribut:6,control:[6,12],convert:[0,1,2,8,10,16,18],coordin:0,copi:17,core:[0,3],core_pb2:0,core_pb2_grpc:0,coroutin:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],correct:[1,3,17],correctli:[0,3],could:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],cours:9,creat:[0,1,2,6,8,9,13,14,15,18,19],create_sess:[0,2,8,14,15,18],credenti:[0,19],creek:9,criteria:[9,18],critic:19,crt:[2,16],curli:12,current:[0,1,5,10],curv:[0,2,8,17],curve_typ:[2,8],custom:[3,4,9,18],d448:18,dai:[0,2,8,10],daili:17,data:[0,2,4,7,8,9,13,14,15,16,17,18],databas:[2,4,8,10,11,16,18],datamodel:0,date:[0,10],datetim:[0,2,8,10,18],dateutil:[2,8],daylight:[0,10],db:[4,16],de:0,def:[1,2,8,14,15,16,18],defaultserverconfig:[2,16],defin:[0,2,9,10,11,12,17],definit:11,delet:0,delete_access_token:0,demonstr:[3,8],depend:[0,1,2,5,8,9,17,19],deprec:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],descend:12,describ:12,design:[4,6,9,13,18],detail:[0,2,3,8],dev:[2,8],develop:[4,5],did:[2,14],differ:[0,2,6,7,8,9,10,14,15],directori:[0,1,6,13,19],discard:[0,2,8],discuss:3,displai:[0,10,19],distinguish:10,distribut:1,divid:[0,10],doc:0,document:[2,5,6,8,12,16,19],doe:[0,1,2,3,10,14,19],domain:0,don:6,done:[0,1,2,8],doubl:[0,10,11,12,17],download:[6,18],driva:9,drop:6,dst:0,dt:[2,8,18],due:6,durat:0,e0903:3,e89b:[2,14],e:[0,1,2,6,8,10,12,16,18],each:[0,1,10,12,18],earlier:[0,6,10],easi:6,edit:5,effici:7,either:[0,2,3,8,12,13,14,15,19],els:1,email:6,email_address:6,empti:[0,10],enabl:[0,1,2,3,5,8,10,15],enabletl:3,encapsul:0,enclos:12,encod:[0,2,16],encrypt:[0,1,13],end:[0,2,8,10,18],end_tim:[0,2,8,10,18],endpoint:12,energi:[0,5],enhanc:19,enough:[0,1,2,16],ent:10,entri:[0,2,8,11],enumer:18,environ:[4,5,15],epoch:[0,17],equal:[0,10,12],error:[0,5,14,18],errordo:0,es:18,especi:10,establish:18,estim:10,etc:[0,10,17],european:[0,10],event:10,ever:0,everi:[1,10],everyth:15,ex:12,exampl:[3,5,6,8,9,10,11,12,14,15,16,17,18,19],examplecompani:[0,1,2,16],except:[0,2,8,16,18],execut:6,exhaust:11,exist:[0,2,10,12,14],exit:0,expect:[0,19],expected_number_of_point:0,expir:1,explain:[13,18],explicit:[0,10],expos:[1,10,18,19],express:[0,2,8,10,11,18],extern:6,extra:[11,17],f:[2,8,12,14,15,18],fail:[5,16],fals:[0,12],fatal:3,featur:[0,1],few:11,field:[0,11],figur:[10,18],file:[2,6,15,16,18,19],financi:10,find:[0,1,2,8,9,10,12,18],finer:[0,10],finish:[0,1,14],finland:[0,10],first:[0,2,3,5,8,10,18,19],fit:[2,16,18],fix:[0,10,19],flag:[0,2,8,17],float64:[2,8],flow:0,follow:[0,2,3,6,8,12,14,15,16,18,19],forc:19,forcast:[0,10],forecast:5,forecast_func:[0,10],forecast_funct:[0,10],forecast_start:0,forecast_start_max:[0,10],forecast_start_min:[0,10],forecastfunct:[0,10],forecastfunctionsasync:[0,10],form:[0,12],format:[0,1,2,8,16,17],formul:[0,10],found:[2,5,14,16,18],foundat:[0,10],frequent:[5,15],from:[0,1,2,8,9,10,12,13,14,15,16,17,18,19],from_arrai:[2,8],full:[0,2,19],full_nam:[0,2,8,10],full_name_timeseri:2,full_vers:[2,15],further:[2,8,13],futur:10,g:[0,1,2,6,8,12,16],gate:9,gather:[2,8],gener:[0,2,3,6,9,16],get:[0,1,8,10,13,15,19],get_all_forecast:[0,10],get_async_connect:0,get_event_loop:[1,2],get_forecast:[0,10],get_mesh_object_inform:18,get_timeseries_attribut:[0,19],get_timeseries_resource_info:0,get_token:0,get_ts_as_of_tim:[0,10],get_ts_historical_vers:[0,10],get_user_ident:[0,1,2],get_vers:[0,2,6,8,15],gettshistoricalvers:[0,10],gettz:8,getuserident:[1,2],getvers:1,git:[5,15,19],github:[5,15,19],give:[0,10],given:[0,2,6,8,9,10,14,18],global:6,glossari:5,go:6,good:6,greater:[2,8],grei:10,group:[9,16],grpc:[0,1,2,5,6,8,13,15,16,18],gsserror:0,guid:[0,2,5,6,18,19],ha:[0,1,2,8,10,13,14,17,18],handl:[0,13],handshak:3,have:[0,1,2,5,6,7,10,11,14,15,17],head:5,help:6,helper:5,here:[5,6,11,15],histor:[0,9,10,19],histori:5,history_funct:[0,10],historyfunct:[0,10],historyfunctionsasync:[0,10],hoc:0,horizont:10,host:[0,1,2,3,6,16,18],hostnam:[0,1,2,16],hour:[0,1,2,8,9,10],hourli:17,how:[0,1,2,5,6,8,9,10,16,18],howev:10,html:0,http:[0,6,15,19],hydro:[9,18],hydropl:18,hydropow:9,i:[0,2,5,8,10,12],id:[0,2,4,6,8,14,18],id_timeseri:2,ident:[0,1],identifi:[0,2,10,14],ignor:[0,10,12],imag:10,implement:8,implicit:11,includ:[0,3,10,17],incom:13,index:5,indic:[2,8,10,16],individu:[2,16],info:[1,2],inform:[0,3,7,8,10,14,15,16,17,18],infrastructur:[4,9],ini_opt:16,initi:[0,6],innerdalsvannet:9,input:[0,12],insecur:[0,13,19],insensit:12,insid:[0,12],instal:[2,4,5,16],instanc:9,instanti:1,instead:[0,8,10],instruct:[3,5,6,16,18],integ:0,integr:[0,4,10],intend:[0,6,19],intens:17,interact:14,interfac:4,intersect:12,interv:[0,2,9,10,18],introduct:5,invalid:0,involv:0,ip:[0,13,18],is_calculation_expression_result:0,is_token_valid:0,issu:[3,5],iter:0,its:[0,9,10,11,15,16],join:6,junitxml:[2,16],just:[1,14,19],kdc:1,keep:0,kei:[0,1],kerbero:[0,1,2,19],kerberos_service_principal_nam:[2,16],kerberostokeniter:0,kerboro:0,kind:[9,13],kit:4,know:6,known:5,laid:0,languag:[0,2,4,9,10],larg:[8,17],larger:[0,10],largest:[0,10],last:[0,2,8,10],later:6,latest:[0,6,10],latter:[0,10],layer:13,learn:[5,8],left:0,len:[2,8,18],less:[0,10],let:[2,8,15],level:9,lib:[0,10],librari:[0,5,6,8,15,17],like:[0,3,9,14,15,17],line:[1,6,10,18],link:0,list:[0,3,10,19],listen:13,local:[0,2,8,10,11,15],local_time_zon:[2,8,18],localhost:[2,16,18],localsystem:[0,1,2,16],locat:0,log:[1,16],logic:12,longer:[0,1,2,14],loos:9,lost:14,lundesokna:9,m:[2,6,15,16,18,19],machin:15,made:[0,10,15,19],mai:[0,1,2,6,8,12],main:[0,1,2,8,14,15,16],maintain:6,major:19,make:[1,2,6,8,12],manag:[0,6,7],mani:[6,9,14],manual:14,mark:16,marker:16,match:[9,12,18],matplotlib:18,max:[0,10],max_number_of_versions_to_get:[0,10],maximum:[0,10],mean:[0,10,12,17],meant:0,measur:[0,2,8,9,11,17],member:0,memori:[5,8,17],mesh:[2,4,11,14,16,17,18],mesh_object:18,mesh_object_attribut:0,mesh_object_id:[0,2,8,18],mesh_server_vers:[2,15],mesh_servic:0,mesh_v2:19,meshobjectid:[0,2,8,10,18],meshservicestub:0,meshtek:18,messag:0,metadata:[17,19],method:[0,1,2,8,10],might:[3,5,9,14,16],millisecond:[0,2,8,17],min15:0,min:[0,10],minor:19,miss:[0,17],model:[0,2,4,7,8,9,12,14,18,19],model_nam:[2,8],modifi:0,modul:[0,5,10],month:0,more:[0,2,5,8,9,10,15,16,19],most:[0,10],move:[17,18],ms:[0,2,8],much:[0,3,9,10],mulligan:18,multipl:[3,6],multipli:[0,10],must:[0,1,2,8,10],n:[12,18],naiv:[0,2,8],name:[0,1,2,6,8,9,10,11,12,15,16,19],namespac:0,nan:[0,2,8,10],need:[0,1,4,5,6,8,9,12,13,16,18,19],neither:3,network:[3,8,13,15],networkservic:[0,1,2,16],new_:0,new_curve_typ:0,new_local_express:0,new_path:0,new_timeseries_entry_id:0,new_unit_of_measur:0,newli:0,next:[0,5,10],nimbu:19,node:9,non:[11,15],none:[0,10,19],normal:14,not_ok:0,note:[0,1,2,10,14,16],noteworthi:5,notic:[2,8],now:[0,2,8,14,15,17],number:[0,2,8,10,11,18],number_of_point:[0,2,8],numpi:17,object:[0,1,2,4,7,8,9,10,11,12,14,18,19],obtain:[0,1],occur:[4,9],offici:6,often:0,ok:[0,2,8],old:0,omit:[0,10],one:[0,2,4,5,6,9,10,14,17],onli:[0,1,2,8,10,12],open:[0,2,8,10,13,14,15,16],openssl_intern:3,oper:[2,8,10],optim:8,optimis:5,option:[0,1,2,8,10,11,12,16,18],oracl:19,order:[4,9],org:[0,6],organ:[2,8],other:[0,5,8,10,11,14],otherwis:[0,12],our:[2,5,6,8],out:[0,1,14,15],output:[2,8,12,15,16],outsid:[0,10],over:[4,5,8,9,13],overridden:11,overwritten:10,own:18,p:[0,10],pa:[0,2,8],packag:[0,2,4,6,8,18],panda:[0,5,8,16,17,18],pandas_datafram:18,pandas_seri:[2,8],paramet:[0,1,2,10],parametr:12,parent:12,parenthesi:10,part:[0,10],pass:[9,16,18],path:[0,2,6,8,12,16,18,19],path_and_pandas_datafram:18,pattern:18,pd:[2,8,18],pem:[0,2,16],per:9,perform:[0,1,4,8,9,10,14],period:[0,4,9,10],permiss:13,physic:[4,9,11,19],pick:[2,8],pictur:[0,10],piecewiselinear:0,ping:3,pip:[6,15,16,18,19],place:10,plant:[9,18],pleas:[0,1,3,8,10,15],plot:18,plot_timeseri:18,poetri:6,point:[0,2,4,8,9,10,12,17,18,19],pointflag:[0,2,8],port:[0,1,2,3,8,13,14,15,16,18],possibl:[0,3,6,11,14],post:18,potenti:[2,8,14],powela:[6,15,19],power:9,practic:18,precis:17,predic:12,prefer:[3,5],prepar:[0,5],present:[0,6,8,10],press:3,previou:[2,8],primari:[9,17],princip:[0,2,16],print:[1,2,8,14,15,18],problem:[3,15,17],procedur:[8,13],process:[0,1,2,7,8,17,18],process_respons:0,produc:12,product:[9,18],production_op:18,program:4,project:[6,15,18],properli:[2,8],properti:[0,9,11],proto:[0,6,8,19],protobuf:6,protocol:[1,8,13,19],prove:1,provid:[0,1,2,6,8,9,13,16,17],purpos:6,push:14,py:[0,1,6,8,10,15,18],pyarg:[2,16],pyarrow:[0,2,8],pycharm:5,pylint:16,pytest:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],python3:[0,10],python:[0,1,2,3,4,10,12,13,14,15,16,17,18],queri:[0,2,8,18,19],question:[5,15],quick:15,quickest:[0,2,15],quickstart:[0,5],quit:17,r:[0,1,2,16],ra:[2,16],rais:0,ran:[5,6],rang:[2,8,9],raw:0,rb:[2,16],re:[5,6],read:[0,3,5,8,16,19],read_timeseries_point:[0,2,8,18,19],read_timeseries_points_async:[0,2],real:18,reason:1,receiv:[0,1,2,18],recommend:[5,15,19],reconnect:14,red:10,refer:[0,1,2,6,8,10,11,12,15],referenc:6,regard:[3,15],regist:[0,1,2,16],reinstal:19,reject:12,rel:[0,10,12],relat:[0,7,10],relationship:9,relative_to:[0,10],releas:6,relev:[0,10],remot:[2,8,13,15],reorgan:19,repli:2,report:[2,3,5,16],repositori:6,repres:[0,4,8,9,10],represent:0,request:[0,1,2,5,8,10,13,14,15,17,18],requir:[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],reservoir:9,reset:0,resolut:[0,2,8,9,10,17],resolv:3,resourc:[0,2,5,14],resources_pb2:0,respect:12,respond:0,respons:[0,8,18],restrict:17,result:[0,1,2,9,10,12,14,18,19],retriev:[0,14,17,18],revok:[0,1,2],revoke_access_token:[0,1,2],revokeaccesstoken:0,rfc:[0,1,2,16],right:[6,15],rollback:[0,2,8,19],root:[0,2,16],root_pem_certif:[0,1,2,8,14,15,16],rout:9,routin:3,rpc:13,rpcerror:[0,2,8,18],run:[0,1,3,5,6,8,10,15,19],run_until_complet:[1,2],runtim:6,runtimeerror:0,s:[0,1,2,3,5,6,9,10,13,16,18],same:[0,2,8,10],save:[0,10,18],save_timeseries_to_csv:18,sc:[2,16],scenario:[17,18],schema:[0,2,8],scm:6,scope:[0,2,10,14],script:[0,6,15,16],sdk:[1,2,3,4,13,16,17,18],search1:12,search2:12,search:[0,4,5,8,9,10,14,18,19],search_for_timeseries_attribut:[0,2,8,18],search_match:18,search_queri:[0,10,18],second:[0,10],section:[2,5,18],secur:[0,1,2,3,13,16,19],see:[0,6,10,12,19],select:6,self_signed_certif:[2,16],send:[0,1,2,8],sensibl:2,sensit:2,sensor:9,sent:[8,18],separ:[4,6,14],sequenc:[4,9],sequenti:[0,2,8],seri:[0,2,4,7,8,9,10,11,14],serial:[0,8],server:[0,1,2,5,6,7,8,10,14,16,17,18,19],server_config:[2,16],server_kerberos_token:0,servic:[0,2,3,13,16],service_princip:0,session:[0,5,8,10,13,15,18,19],session_id:[0,2,14],set:[0,2,3,6,8,10,11,12,13,14,15,18,19],setup:[5,15,18,19],sever:[0,10,17],share:[0,5,8,14],shell:6,shift:[2,8],ship:16,should:[0,2,3,6,10,12,13,14,15,16],show:[0,1,2,8,10,14,15,16,18],show_plot:18,sight:1,signal:0,signal_final_response_receiv:0,simplethermaltestmodel:[2,8],simplethermaltestresourcecatalog:2,sinc:[0,17],singl:[0,10,12],size:17,smallest:[0,10],sme:[6,15,19],so:[2,6,8,9,16],socket:0,softwar:[0,4,7],some:[0,2,3,4,5,6,8,9,10,11,12,14,15,16,17,18],some_python_packag:6,some_tzinfo:8,somepowerplantchimney2:[2,8],someth:[0,9,11],sourc:[0,6,10],special:17,specif:[0,6,9,10,11,12,14,18],specifi:[0,2,10,12,16],sphinx_copybutton:16,spn:[0,1],squar:12,src:[3,6],ssl:3,ssl_error_ssl:5,ssl_transport_secur:3,staircas:0,staircasestartofstep:0,standard:[0,2,6,8,10],start:[0,2,8,9,10,12,15,18,19],start_and_end_sess:[0,2,8],start_object_guid:[0,2,18],start_object_path:[0,2,8],start_tim:[0,2,8,10,18],state:[0,10],statement:[0,2,14],statist:5,statistical_funct:[0,10],statisticalfunct:[0,10],statisticalfunctionsasync:[0,10],statu:[0,9,10],steal:14,step:[2,5,6,8,12,17],still:0,storag:[0,6],store:[0,11,14,17],storfossdammen:9,str:[0,2,8,10],stream:0,string:[0,2,10,16],structur:12,subsequ:[0,1],subset:[2,16],success:[1,4,9],successfulli:[1,2],suffic:6,suffix:12,suggest:[3,6],sum:[0,2,8,9,10],sum_single_timeseri:[0,10],sumi:[0,10],summari:[0,10],suppli:18,support:[0,1,6,8,13,15,17],sure:[1,2,8],symbol:10,synchron:[0,1,2,10],syntax:[2,4,5,9],system:[1,2,6,7,8,9,14],t:[0,6,10,19],tabl:[0,2,8,10],tailor:18,take:[0,1,2,8,10,12],target:[0,10],task:[0,2,4,8,9,18],tekicc_st:18,templat:11,tempor:13,temporari:[10,14],termin:6,test:[4,5,6,18,19],test_aio_connect:0,test_async_connection_get_user_ident:0,test_async_connection_revoke_access_token:0,test_async_get_vers:0,test_auth_metadata_plugin_obtains_correctly_new_token_after_delet:0,test_auth_metadata_plugin_obtains_valid_token_in_init:0,test_authent:0,test_can_connect_to_existing_sess:0,test_can_create_empty_timeseri:[0,2,16],test_can_create_timeserie_from_existing_data:0,test_can_serialize_and_deserialize_write_timeserie_request:0,test_commit:0,test_connect:0,test_connection_get_user_ident:0,test_connection_revoke_access_token:0,test_delete_access_token:0,test_exampl:0,test_forecast_get_all_forecast:0,test_forecast_get_forecast:0,test_get_timeseri:0,test_get_timeseries_async:0,test_get_vers:0,test_history_get_ts_as_of_tim:0,test_history_get_ts_historical_vers:0,test_is_grpc_respond:0,test_is_valid_token_returns_false_for_deleted_access_token:0,test_open_and_close_sess:0,test_read_timeseries_attribut:0,test_read_timeseries_attribute_async:0,test_read_timeseries_point:0,test_read_timeseries_points_async:0,test_read_timeseries_points_with_different_datetime_timezon:0,test_read_timeseries_points_with_different_datetime_timezones_async:0,test_read_timeseries_points_without_specifying_timeseries_should_throw:0,test_read_transformed_timeseries_point:0,test_read_transformed_timeseries_points_with_uuid:0,test_rollback:0,test_run_example_script:0,test_search_timeseries_attribut:0,test_search_timeseries_attribute_async:0,test_sess:0,test_sessions_using_async_contextmanag:0,test_sessions_using_contextmanag:0,test_statistical_sum:0,test_statistical_sum_single_timeseri:0,test_timeseri:[0,2,16],test_update_timeseries_attribute_with_timeseriescalcul:0,test_update_timeseries_attribute_with_timeseriescalculation_async:0,test_update_timeseries_attribute_with_timeseriesrefer:0,test_update_timeseries_attribute_with_timeseriesreference_async:0,test_update_timeseries_entri:0,test_update_timeseries_entry_async:0,test_util:[2,16],test_write_timeseries_point:0,test_write_timeseries_points_async:0,test_write_timeseries_points_using_timskey_async:0,test_write_timeseries_points_with_different_pyarrow_table_datetime_timezon:0,test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones_async:0,text:12,than:[0,2,8,10,11],thei:[0,2,6,8,9,12,16],them:[0,2,5,6,8,11,16,17],theme:9,thermalcompon:[2,8],thi:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],thing:[3,14],think:5,those:9,three:[0,10],through:13,thrown:0,time:[0,1,2,4,5,7,9,10,11,14,18],timedelta:8,timeseri:[0,5,8,10,15,18,19],timeseries_attribut:[2,8],timeseries_full_nam:2,timeseries_id:2,timeseries_oper:[0,8],timeseries_read:[2,8],timeseriesattribut:0,timeseriesentri:0,timeseriesentryid:0,timestamp:[0,2,8,10,17],timezon:[0,2,8,10,18],timskei:[0,2,19],tl:[0,1,2,3,13,19],to_datetim:[2,8,18],to_panda:[2,8,18],todo:[0,15],token:[0,2,13],tool:[4,6,16],toward:[1,19],tracker:[3,5],transform:[2,5,8,9,19],transform_funct:[0,2,8,10],transformed_timeseri:[2,8],transformfunct:[0,10],transformfunctionsasync:[0,10],transport:13,travers:[2,4,9],treat:[0,2,8],tree:9,trend:10,troubl:5,ts:[0,10],tsi:3,tsrawatt:[2,8],turn:3,two:[0,1,2,6,8,10],type:[0,2,8,10,11,17,18],typeerror:0,tz:[2,8],tz_convert:[2,8,18],tzinfo:[2,8,18],tzlocal:[2,8],uint32:[0,2,8],underli:11,understand:7,union:12,uniqu:0,unit:[0,2,8,9,11,17],unit_of_measur:[2,8],unittest:[2,16],univers:0,unix:[0,2,8,17],unknown:0,unless:[0,6,10],unprotect:10,unspecifi:0,until:[1,14],up:[0,3,6,15,18],updat:[0,19],update_timeseries_attribut:0,update_timeseries_resource_info:[0,19],upn:1,us:[0,1,3,4,5,6,7,8,9,10,12,13,14,15,16,17,19],use_cas:18,use_case_1:18,use_case_nam:18,usecas:19,user:[0,1,2,5,8,13,14,16,19],user_ident:[1,2],user_princip:0,userident:0,usr:[0,10],usual:1,utc:[0,2,8,10,17,18],utc_tim:[0,2,8,18],uuid:[0,2,14,18],uuid_id:[0,2,8],v1alpha:0,valid:[0,1,10,11,14],valu:[0,2,8,9,10,11,17],variabl:[10,15],variou:[10,19],venv:4,verbos:[2,16],verifi:[0,3,16],version:[0,1,4,6,8,10,15],version_info:2,versioninfo:0,vertic:10,via:10,view:[6,14],virtual:[4,6,15],visual:[18,19],volu:[1,2,3,5,6,8,10,12,13,14,15,16],vs:8,vv:[2,16],wa:0,wai:[0,2,6,8,10,13,14,15],wait:[0,8],walk:12,want:[0,1,2,6,9,14,15,18],warn:[2,14,16],water:9,we:[1,2,6,15,18],weather:10,week:0,were:18,what:[0,2,5,10,16],when:[0,1,2,3,6,10,12,13,14,19],where:[6,9,12,14],which:[0,2,8,9,10,11,12,13,14,15,16,18],whose:12,wide:9,win:0,window:[1,6],winkerbero:[0,1,2,16],with_full_nam:[0,2,8],with_timskei:0,with_uuid_id:[0,2,18],within:[0,2,10,12,13,14,15],without:[0,1,2,3,10,14,16],wizard:6,won:19,work:[0,1,4,5,6,7,8,10,14,18,19],workspac:[13,14],would:[0,1,2,16],write:[0,4,5,6,8,10,16,19],write_timeseries_point:[0,2,8],write_timeseries_points_async:0,written:[0,2,8,16],wrong:5,wrong_version_numb:3,xml:[2,16],year:0,yet:[0,2,8],yield:0,you:[0,1,2,3,5,6,8,10,12,13,14,15,16,18,19],your:[1,2,3,5,6,15,16,18],your_python_script:6,zone:[0,2,10,18]},titles:["API documentation","Authentication","Examples","Frequently Asked Questions","Glossary","Welcome to Mesh Python SDK","Installation","An introduction to Mesh","Mesh Python SDK","Mesh concepts","Mesh functions","Attributes","Mesh search language","Mesh server","Session","Quickstart guide","Tests","Time series","Use cases","Versions"],titleterms:{"0":19,"2":19,"3":19,"case":18,"do":3,"function":[0,10,18],"new":19,The:18,add:18,aio:0,alpha:19,am:3,an:7,api:0,ask:3,asynchron:2,attribut:[2,11],authent:1,author:2,bug:3,calc:0,calcul:[0,10],call:15,chang:19,combin:12,compat:19,concept:9,configur:[3,18],connect:[2,3],criteria:12,date:8,definit:10,depend:[6,18],develop:6,document:0,edit:18,environ:6,error:3,exampl:[0,1,2],fail:3,featur:[3,5,19],first:15,forecast:[0,10],found:3,frequent:3,get:[2,3,5,18],git:6,github:6,glossari:4,grpc:3,guid:15,have:3,help:[3,5],helper:18,histori:[0,10],i:3,indic:5,instal:[6,15,18,19],instruct:19,introduct:7,issu:19,known:19,languag:12,mesh:[0,1,3,5,6,7,8,9,10,12,13,15,19],more:3,multipl:12,need:3,next:15,one:3,oper:12,other:3,panda:2,prefer:18,prepar:16,prerequisit:[5,15],princip:1,pycharm:6,python:[5,6,8,19],queri:12,question:3,quickstart:[2,15],ran:3,read:2,recommend:6,refer:5,request:3,requir:1,run:[2,16,18],sdk:[5,6,8,19],search:[2,12],seri:17,server:[3,13,15],servic:1,session:[2,14],setup:6,ssl_error_ssl:3,start:5,statist:[0,10],step:15,syntax:12,tabl:5,test:[0,2,3,16],them:3,think:3,time:[8,17],timeseri:2,token:1,transform:[0,10],travers:12,us:[2,18],usag:1,user:6,version:[2,5,19],volu:0,welcom:5,what:3,work:2,write:2,wrong:3,zone:8}})