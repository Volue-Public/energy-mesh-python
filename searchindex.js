Search.setIndex({docnames:["api","authentication","examples","faq","glossary","index","installation","introduction_to_mesh","mesh_client","mesh_concepts","mesh_functions","mesh_object_attributes","mesh_search","mesh_server","quickstart","tests","timeseries","usecases","versions"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api.rst","authentication.rst","examples.rst","faq.rst","glossary.rst","index.rst","installation.rst","introduction_to_mesh.rst","mesh_client.rst","mesh_concepts.rst","mesh_functions.rst","mesh_object_attributes.rst","mesh_search.rst","mesh_server.rst","quickstart.rst","tests.rst","timeseries.rst","usecases.rst","versions.rst"],objects:{"volue.mesh":[[0,1,1,"","Authentication"],[0,1,1,"","Connection"],[0,1,1,"","Credentials"],[0,1,1,"","Timeseries"],[0,0,0,"-","aio"],[0,0,0,"-","calc"],[0,0,0,"-","examples"],[0,0,0,"-","tests"]],"volue.mesh.Authentication":[[0,1,1,"","KerberosTokenIterator"],[0,1,1,"","Parameters"],[0,2,1,"","delete_access_token"],[0,2,1,"","get_token"],[0,2,1,"","is_token_valid"]],"volue.mesh.Authentication.KerberosTokenIterator":[[0,2,1,"","process_response"],[0,2,1,"","signal_final_response_received"]],"volue.mesh.Authentication.Parameters":[[0,3,1,"","service_principal"],[0,3,1,"","user_principal"]],"volue.mesh.Connection":[[0,1,1,"","Session"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.Connection.Session":[[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","history_functions"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","statistical_functions"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.Timeseries":[[0,1,1,"","Curve"],[0,1,1,"","PointFlags"],[0,1,1,"","Resolution"],[0,4,1,"","is_calculation_expression_result"],[0,4,1,"","number_of_points"],[0,3,1,"","schema"]],"volue.mesh.Timeseries.Curve":[[0,3,1,"","PIECEWISELINEAR"],[0,3,1,"","STAIRCASE"],[0,3,1,"","STAIRCASESTARTOFSTEP"],[0,3,1,"","UNKNOWN"]],"volue.mesh.Timeseries.PointFlags":[[0,3,1,"","MISSING"],[0,3,1,"","NOT_OK"],[0,3,1,"","OK"]],"volue.mesh.Timeseries.Resolution":[[0,3,1,"","BREAKPOINT"],[0,3,1,"","DAY"],[0,3,1,"","HOUR"],[0,3,1,"","MIN15"],[0,3,1,"","MONTH"],[0,3,1,"","UNSPECIFIED"],[0,3,1,"","WEEK"],[0,3,1,"","YEAR"]],"volue.mesh.aio":[[0,1,1,"","Connection"]],"volue.mesh.aio.Connection":[[0,1,1,"","Session"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.aio.Connection.Session":[[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","history_functions"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","statistical_functions"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.calc":[[0,0,0,"-","common"],[0,0,0,"-","history"],[0,0,0,"-","statistical"],[0,0,0,"-","transform"]],"volue.mesh.calc.common":[[0,1,1,"","Timezone"]],"volue.mesh.calc.common.Timezone":[[0,3,1,"","LOCAL"],[0,3,1,"","STANDARD"],[0,3,1,"","UTC"]],"volue.mesh.calc.history":[[0,1,1,"","HistoryFunctions"],[0,1,1,"","HistoryFunctionsAsync"]],"volue.mesh.calc.history.HistoryFunctions":[[0,2,1,"","get_all_forecasts"],[0,2,1,"","get_forecast"],[0,2,1,"","get_ts_as_of_time"],[0,2,1,"","get_ts_historical_versions"]],"volue.mesh.calc.history.HistoryFunctionsAsync":[[0,2,1,"","get_all_forecasts"],[0,2,1,"","get_forecast"],[0,2,1,"","get_ts_as_of_time"],[0,2,1,"","get_ts_historical_versions"]],"volue.mesh.calc.statistical":[[0,1,1,"","StatisticalFunctions"],[0,1,1,"","StatisticalFunctionsAsync"]],"volue.mesh.calc.statistical.StatisticalFunctions":[[0,2,1,"","sum"]],"volue.mesh.calc.statistical.StatisticalFunctionsAsync":[[0,2,1,"","sum"]],"volue.mesh.calc.transform":[[0,1,1,"","Method"],[0,1,1,"","Parameters"]],"volue.mesh.calc.transform.Method":[[0,3,1,"","AVG"],[0,3,1,"","AVGI"],[0,3,1,"","FIRST"],[0,3,1,"","LAST"],[0,3,1,"","MAX"],[0,3,1,"","MIN"],[0,3,1,"","SUM"],[0,3,1,"","SUMI"]],"volue.mesh.calc.transform.Parameters":[[0,3,1,"","method"],[0,3,1,"","resolution"],[0,3,1,"","timezone"]],"volue.mesh.examples":[[0,0,0,"-","connect_asynchronously"],[0,0,0,"-","connect_synchronously"],[0,0,0,"-","get_version"],[0,0,0,"-","quickstart"],[0,0,0,"-","read_timeseries_points"],[0,0,0,"-","read_timeseries_points_async"],[0,0,0,"-","timeseries_operations"],[0,0,0,"-","write_timeseries_points"],[0,0,0,"-","write_timeseries_points_async"]],"volue.mesh.examples.connect_asynchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.connect_synchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.get_version":[[0,5,1,"","main"]],"volue.mesh.examples.quickstart":[[0,5,1,"","main"]],"volue.mesh.examples.read_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points"]],"volue.mesh.examples.read_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points_async"]],"volue.mesh.examples.timeseries_operations":[[0,5,1,"","main"]],"volue.mesh.examples.write_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.examples.write_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.tests":[[0,0,0,"-","test_aio_connection"],[0,0,0,"-","test_authentication"],[0,0,0,"-","test_connection"],[0,0,0,"-","test_examples"],[0,0,0,"-","test_session"],[0,0,0,"-","test_timeseries"]],"volue.mesh.tests.test_aio_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_get_timeseries_async"],[0,5,1,"","test_history_get_all_forecasts"],[0,5,1,"","test_history_get_forecast"],[0,5,1,"","test_history_get_ts_as_of_time"],[0,5,1,"","test_history_get_ts_historical_versions"],[0,5,1,"","test_read_timeseries_attribute_async"],[0,5,1,"","test_read_timeseries_points_async"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute_async"],[0,5,1,"","test_statistical_sum"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation_async"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference_async"],[0,5,1,"","test_update_timeseries_entry_async"],[0,5,1,"","test_write_timeseries_points_async"],[0,5,1,"","test_write_timeseries_points_using_timskey_async"]],"volue.mesh.tests.test_authentication":[[0,5,1,"","aconnection"],[0,5,1,"","auth_metadata_plugin"],[0,5,1,"","connection"],[0,5,1,"","test_async_connection_get_user_identity"],[0,5,1,"","test_async_connection_revoke_access_token"],[0,5,1,"","test_auth_metadata_plugin_obtains_correctly_new_token_after_delete"],[0,5,1,"","test_auth_metadata_plugin_obtains_valid_token_in_init"],[0,5,1,"","test_connection_get_user_identity"],[0,5,1,"","test_connection_revoke_access_token"],[0,5,1,"","test_delete_access_token"],[0,5,1,"","test_is_valid_token_returns_false_for_deleted_access_token"]],"volue.mesh.tests.test_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_get_timeseries"],[0,5,1,"","test_history_get_all_forecasts"],[0,5,1,"","test_history_get_forecast"],[0,5,1,"","test_history_get_ts_as_of_time"],[0,5,1,"","test_history_get_ts_historical_versions"],[0,5,1,"","test_read_timeseries_attribute"],[0,5,1,"","test_read_timeseries_points"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute"],[0,5,1,"","test_statistical_sum"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference"],[0,5,1,"","test_update_timeseries_entry"],[0,5,1,"","test_write_timeseries_points"]],"volue.mesh.tests.test_examples":[[0,5,1,"","test_is_grpc_responding"],[0,5,1,"","test_run_example_scripts"]],"volue.mesh.tests.test_session":[[0,5,1,"","test_async_get_version"],[0,5,1,"","test_can_connect_to_existing_session"],[0,5,1,"","test_get_version"],[0,5,1,"","test_open_and_close_session"],[0,5,1,"","test_sessions_using_async_contextmanager"],[0,5,1,"","test_sessions_using_contextmanager"]],"volue.mesh.tests.test_timeseries":[[0,5,1,"","test_can_create_empty_timeserie"],[0,5,1,"","test_can_create_timeserie_from_existing_data"],[0,5,1,"","test_can_serialize_and_deserialize_write_timeserie_request"]],volue:[[0,0,0,"-","mesh"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","property","Python property"],"5":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:property","5":"py:function"},terms:{"0":[0,2,5,8,10,14,15],"0000":2,"000000000000":2,"00000003":2,"0000000b":2,"0001":2,"0003":2,"01":16,"09":3,"1":[0,1,2,5,6,8,10,14,15,17,18],"10":[2,17],"100":18,"1000":2,"100000f7":3,"101":18,"102":18,"1073741824":0,"109":18,"115":18,"116":18,"12":[2,8,18],"120":18,"122":18,"125":18,"133":18,"134":18,"135":18,"138":18,"1468":3,"1970":16,"2":[0,2,5,8,10],"2016":2,"2021":17,"2078":[1,2,15],"24":2,"26":3,"29912":3,"3":[0,2,5,6,10,14,15],"32":16,"3ecf8ab0e2d4":17,"4":[0,2,15],"4299":17,"5":[0,2,8,10],"50051":[2,14,15,17],"55":10,"59":3,"6":[0,2,10],"667000000":3,"67108864":0,"7":[0,5,6,10,14,18],"72":2,"8":[0,2,5,6,10,14,18],"801896b0":17,"874a":17,"9":[5,6,14,17,18],"99":14,"byte":[0,2,15],"case":[0,1,2,3,5,8,12,14,15,18],"class":[0,10],"default":[6,11,14],"do":[2,5,6,15,17],"enum":0,"final":[0,17],"float":16,"function":[0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,18],"import":[1,2,7,8,14,15],"int":[0,2,10],"long":8,"new":[0,1,5,6,12,17],"return":[0,2,10,18],"throw":0,"true":[3,12,17],"try":[0,2,3,5,17],"while":8,A:[2,4,8,9,10,11,12,16],AND:12,As:6,For:[1,3,6,8,9,12,14],If:[0,1,2,3,5,6,10,11,12,14,15],In:[0,3,14,15],Is:3,It:[0,1,10,12,14,16],No:[0,2],OR:[2,12],One:9,Or:[1,2,6],The:[0,1,2,5,6,8,9,10,11,12,14,15,16],Then:17,There:[6,9],These:[2,6,9,15,17],To:[1,5,6,7,9,12,15,17],__main__:[1,2,8,14,15],__name__:[1,2,8,14,15],_authent:0,_common:[0,10],_connect:0,_get_connection_info:[1,2,8,14],_timeseri:[0,10],abl:[6,7,9,12,15,17],about:[17,18],abov:3,accept:[2,12,18],access:[0,1,2,6,10,12],account:[1,2,15],aconnect:[0,1,2],acquir:[0,16],action:1,activ:[1,6,18],ad:[0,1,2,11,15,18],add:[5,6],addit:[1,6,11,17],address:[0,1,2,3,6,8,14,15,17],after:[0,1,6,16],aio:[1,2,5,8],aka:[9,11],aliv:0,all:[0,1,2,3,6,9,10,11,12,15,16,17],allevi:16,allow:15,along:6,alpha:5,also:[1,6],alwai:12,am:5,an:[0,2,5,6,9,10,11,12,14,17],ani:[0,1,2,3,8,9,10,11,16],anoth:[9,16],anyon:1,apach:[5,6,16],api:[1,4,5,12],append:[2,17],appli:12,applic:4,ar:[0,1,2,3,5,6,9,10,11,12,14,15,16,17],arbitrari:6,architectur:7,area:[4,9],argument:[0,10],arrai:[0,2,10],arrang:9,arrow:[2,5,6,16],arrow_t:[2,17],ask:[5,14],asset:[4,9],associ:16,assum:14,async:[0,2,5,8,10],asyncconnect:[0,1,2],asynchron:[0,1,5],asyncio:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],attribut:[0,5,9,12],attributenam:12,auth_metadata_plugin:0,authent:[0,2,3,15,18],authenticatekerbero:[0,1],authentication_paramet:[0,1,2],author:[0,1,5],automat:[1,18],avail:[6,9,10,15],available_at_timepoint:[0,10],avg:[0,10],avgi:[0,10],await:[2,5,8],b:[2,8,10],back:8,base:[2,3,6,7,9,10,12],basic:[4,7],becaus:[0,1],been:16,behav:[0,18],believ:3,besid:16,between:[0,9,12],bit:16,board:3,bool:0,both:[0,2,16,18],bracket:12,breakpoint:[0,16],bring:6,bug:[5,18],build:[6,9],build_dat:14,c:[2,15],cach:15,calc:[2,5,10,12],calcul:[0,4,9,10,11,12],call:[0,1,2,5,6,11],can:[0,1,2,3,6,8,9,10,11,12,14,15,16],cancel:0,categori:[0,10],caus:3,cc:3,center:1,cert:[2,15],certain:0,certif:[2,15],challeng:0,chang:[0,2,3,5,6,14,15],channel_credenti:0,channelcredenti:0,charact:[1,2,10,12,15],check:[0,2,3,14],child:12,children:2,chimney2timeseriesraw:2,clean:0,click:6,client:[0,1,2,3,5,7],clone:6,close:[0,2,8,14],closest:12,cloud:6,cmd:[2,15],code:[0,2,3,6,14],collect:[4,9,12],com:[1,2,6,14,15,18],combin:[0,10,11],come:[6,9],command:[6,17],commit:[0,2,14,18],common:[0,2,10,16],commun:[1,2,5,6,8,14,17,18],compani:[1,2,15],companyad:[1,2,15],comparison:12,compat:5,complet:0,composit:12,compound_stmt:0,concept:[0,4,6,7,8],concurr:[0,2,8],confidenti:3,config:6,configur:[0,1,2,5,6,14],confirm:1,connect:[0,1,5,9,11,14,15,17,18],connect_asynchron:0,connect_synchron:0,connect_to_sess:0,consist:[1,7,11,12,16],consolid:4,consult:[1,3,14],consum:16,contact:[1,3,14],contain:[0,2,9,17],context:0,contextmanag:0,contribut:6,control:[6,12],convert:[0,1,2,15],coordin:0,copi:16,core:[0,3],core_pb2:0,core_pb2_grpc:0,coroutin:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],correct:[1,3,16],correctli:[0,3],could:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],cours:9,creat:[0,1,2,6,8,9,14,17,18],create_sess:[0,2,8,14,17],credenti:[0,18],creek:9,criteria:[9,17],critic:18,crt:[2,15],csv:17,curli:12,current:[0,1,5],curv:[0,2,16],curve_typ:2,custom:[3,4,9,17],d448:17,dai:[0,2],daili:16,data:[0,2,4,7,9,14,15,16,17],databas:[2,4,10,11,15,17],datamodel:0,datetim:[0,2,10,17],daylight:0,db:[4,15],de:0,def:[1,2,8,14,15,17],defaultserverconfig:[2,15],defin:[2,9,11,12,16],definit:11,delet:0,delete_access_token:0,demonstr:[3,8],depend:[0,1,5,8,9,16,18],deprec:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],descend:12,describ:12,design:[4,6,9,17],detail:[0,3],dev:[2,8],develop:[4,5],differ:[0,6,7,9,10,14],directori:[1,18],discard:[0,2],discuss:3,displai:18,distinguish:10,distribut:1,doc:0,document:[5,6,12,15,18],doe:[0,1,3,10,18],don:6,done:[0,1,2,8],doubl:[0,10,11,12,16],download:[6,17],driva:9,drop:6,dst:0,due:6,durat:0,e0903:3,e:[0,1,2,6,10,12,15,17],each:[0,1,10,12,17],earlier:6,easi:6,edit:5,effici:7,either:[0,3,12,14,18],els:1,email:6,email_address:6,empti:[0,10],enabl:[1,2,3,5,8,14],enabletl:3,enclos:12,encod:[2,15],encrypt:1,end:[0,2,8,17],end_tim:[0,2,10,17],endpoint:12,energi:[0,5],enhanc:18,enough:[1,2,15],ent:10,entri:[0,2,11],enumer:[0,17],environ:[4,5,14],epoch:16,equal:[0,10,12],error:[0,5,17],es:17,establish:17,etc:[0,16],ever:0,everi:[1,10],everyth:14,ex:12,exampl:[3,5,6,8,9,10,11,12,14,15,16,17,18],examplecompani:[1,2,15],except:[0,2,15,17],execut:6,exhaust:11,exist:[0,12],exit:0,expect:[0,18],expected_number_of_point:0,expir:1,explain:17,expos:[1,17,18],express:[0,2,10,11,17],extern:6,extra:[11,16],f:[2,8,12,14,17],fail:[5,15],fals:[0,12],fatal:3,featur:[0,1],few:11,field:[0,10,11],figur:17,file:[2,6,14,15,17,18],find:[0,1,2,9,10,12,17],finish:1,first:[0,2,3,5,10,17,18],fit:[2,15,17],fix:18,flag:[0,2,16],float64:2,flow:0,follow:[0,2,3,6,8,10,12,14,15,17,18],forc:18,forecast:[0,10],forecast_start:0,forecast_start_max:[0,10],forecast_start_min:[0,10],form:12,format:[0,1,2,15,16],found:[2,5,15,17],frequent:[5,14],from:[0,1,2,8,9,10,12,14,15,16,17,18],from_arrai:2,full:[2,18],full_nam:[0,2,10],full_name_timeseri:2,full_vers:[2,14],further:2,g:[0,1,2,6,12,15],gate:9,gather:[2,8],gener:[0,2,3,6,9,15],get:[0,1,8,14,18],get_all_forecast:[0,10],get_event_loop:[1,2],get_forecast:[0,10],get_mesh_object_inform:17,get_timeseries_attribut:[0,18],get_timeseries_resource_info:0,get_token:0,get_ts_as_of_tim:[0,10],get_ts_historical_vers:[0,10],get_user_ident:[0,1,2],get_vers:[0,2,6,8,14],getuserident:[1,2],getvers:1,git:[5,14,18],github:[5,14,18],given:[0,2,6,9,10,17],global:6,glossari:5,go:6,good:6,greater:2,group:[9,15],grpc:[0,1,2,5,6,8,10,14,15,17],gsserror:0,guid:[0,2,5,6,17,18],ha:[0,1,2,10,16,17],handshak:3,have:[0,1,2,5,6,7,10,11,14,16],head:5,help:6,helper:5,here:[5,6,11,14],histor:[0,9,10,18],histori:0,history_funct:0,historyfunct:[0,10],historyfunctionsasync:[0,10],hoc:0,host:[0,1,2,3,6,15,17],hostnam:[1,2,15],hour:[0,1,2,9],hourli:16,how:[0,1,2,5,6,8,9,15,17],howev:10,html:0,http:[0,6,14,18],hydro:[9,17],hydropl:17,hydropow:9,i:[2,5,10,12],id:[2,4,6,17],id_timeseri:2,ident:[0,1],identifi:[2,10],ignor:12,implement:8,implicit:11,includ:[0,3,10,16],index:5,indic:[2,8,15],individu:[2,15],info:[1,2],inform:[0,3,7,14,15,16,17],infrastructur:[4,9],ini_opt:15,initi:6,innerdalsvannet:9,input:12,insecur:18,insensit:12,insid:[0,12],instal:[2,4,5,15],instanc:9,instanti:1,instead:[0,10],instruct:[3,5,6,15,17],integr:4,intend:[0,6,18],intens:16,interfac:4,intersect:12,interv:[0,2,9,10,17],introduct:5,invalid:0,ip:17,is_calculation_expression_result:0,is_token_valid:0,issu:[3,5],iter:0,its:[0,9,10,11,14,15],join:6,junitxml:[2,15],just:[1,18],kdc:1,keep:0,kei:1,kerbero:[0,1,2,18],kerberos_service_principal_nam:[2,15],kerberostokeniter:0,kind:9,kit:4,know:6,known:5,languag:[0,2,4,9,10],larg:16,larger:[0,10],last:[0,2,10],later:6,latest:6,learn:5,left:0,len:[2,17],less:[0,10],let:[2,8,14],level:9,lib:[0,10],librari:[0,5,6,8,14,16],like:[0,3,9,14,16],line:[1,6,17],list:[0,3,10,18],local:[0,11,14],localhost:[2,15,17],localsystem:[1,2,15],log:[1,15],logic:12,longer:[0,1,2],loos:9,lundesokna:9,m:[2,6,14,15,17,18],machin:14,made:[0,10,14,18],mai:[0,1,6,8,12],main:[0,1,2,8,14,15],maintain:6,major:18,make:[1,2,6,12],manag:[0,6,7],mani:[6,9],mark:15,marker:15,match:[9,12,17],matplotlib:17,max:[0,10],max_number_of_versions_to_get:[0,10],mean:[0,12,16],meant:0,measur:[2,9,11,16],member:0,memori:[5,16],mesh:[2,4,11,15,16,17],mesh_object:17,mesh_server_vers:[2,14],mesh_servic:0,mesh_v2:18,meshobjectid:[0,10],meshservicestub:0,meshtek:17,metadata:[16,18],method:[0,1,2,10],might:[3,5,9,15],millisecond:[2,16],min15:0,min:[0,10],minor:18,misc:0,miss:[0,16],model:[0,2,4,7,9,12,17,18],model_nam:2,modul:[0,5,10],month:0,more:[0,5,9,14,15,18],move:[16,17],ms:[0,2],much:[3,9],mulligan:17,multipl:[3,6],must:[1,2],n:[12,17],name:[1,2,6,9,10,11,12,14,15,18],namespac:0,nan:[0,10],need:[0,1,4,5,6,9,12,15,17,18],neither:3,network:[3,8,14],networkservic:[1,2,15],new_:0,new_curve_typ:0,new_local_express:0,new_path:0,new_timeseries_entry_id:0,new_unit_of_measur:0,newli:0,next:[0,5,10],nimbu:18,node:9,non:[11,14],none:[0,10,18],not_ok:0,note:[0,1,2,15],noteworthi:5,now:[2,14,16],number:[0,2,10,11,17],number_of_point:[0,2],numpi:16,object:[0,1,2,4,7,9,10,11,12,17,18],obtain:[0,1],occur:[4,9],offici:6,ok:[0,2],old:0,one:[0,4,5,6,9,16],onli:[0,1,2,10,12],open:[0,2,8,10,14,15],openssl_intern:3,oper:2,optimis:5,option:[0,1,2,10,11,12,15,17],oracl:18,order:[4,9],org:[0,6],organ:2,other:[0,5,8,11],otherwis:12,our:[2,5,6],out:[1,14],output:[2,8,12,14,15],outsid:[0,10],over:[4,5,8,9],overridden:11,own:17,pa:2,packag:[0,2,4,6,8,17],panda:[0,5,15,16,17],pandas_datafram:17,pandas_seri:2,param:0,paramet:[0,1,2,10],parametr:12,parent:12,parenthesi:10,pass:[9,15,17],path:[0,2,6,12,15,17,18],path_and_pandas_datafram:17,pattern:17,pem:[2,15],per:9,perform:[1,4,8,9],period:[0,4,9,10],physic:[4,9,11,18],pick:2,piecewiselinear:0,ping:3,pip:[6,14,15,17,18],place:10,plant:[9,17],pleas:[1,3,14],plot:17,plot_timeseri:17,poetri:6,point:[0,2,4,9,10,12,16,17,18],pointflag:[0,2],port:[0,1,2,3,8,14,15,17],possibl:[0,3,6,11],post:17,powela:[6,14,18],power:9,practic:17,precis:16,predic:12,prefer:[3,5],prepar:[0,5],present:6,press:3,primari:[9,16],princip:[2,15],print:[1,2,8,14,17],problem:[3,14,16],process:[0,1,2,7,8,16,17],process_respons:0,produc:12,product:[9,17],production_op:17,program:4,project:[6,14,17],properti:[0,9,11],proto:[0,6,18],protobuf:6,protocol:[1,18],prove:1,provid:[0,1,2,6,9,10,15,16],purpos:6,py:[0,1,6,10,14,17],pyarg:[2,15],pyarrow:[0,2],pycharm:5,pytest:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],python3:[0,10],python:[0,1,2,3,4,8,10,12,14,15,16,17],queri:[0,2,17,18],question:[5,14],quick:14,quickest:[0,2,14],quickstart:[0,5],quit:16,r:[1,2,15],ra:[2,15],rais:[0,10],ran:[5,6],rang:[2,9],rb:[2,15],re:[5,6],read:[0,3,5,10,15,18],read_timeseries_point:[0,2,10,17,18],read_timeseries_points_async:[0,2],real:17,reason:1,receiv:[0,1,2,17],recommend:[5,14,18],refer:[0,1,6,11,12,14],referenc:6,regard:[3,14],regist:[1,2,15],reinstal:18,reject:12,rel:12,relat:7,relationship:9,relative_to:[0,10],releas:6,relev:[0,10],remot:[2,14],reorgan:18,repli:2,report:[2,3,5,15],repositori:6,repres:[4,9],request:[0,1,2,5,8,10,14,16,17],requir:[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],reservoir:9,reset:0,resolut:[0,2,9,10,16],resolv:3,resourc:[2,5],resources_pb2:0,respect:12,respond:0,respons:[0,8,17],restrict:16,result:[0,1,2,9,10,12,17,18],retriev:[0,16,17],revok:[0,1,2],revoke_access_token:[0,1,2],revokeaccesstoken:0,rfc:[1,2,15],right:[6,14],rollback:[0,2,18],root:[2,15],root_pem_certif:[0,1,2,8,14,15],rout:9,routin:3,rpcerror:[0,2,10,17],run:[0,1,3,5,6,8,10,14,18],run_until_complet:[1,2],runtim:6,runtimeerror:[0,10],s:[0,1,2,3,5,6,9,10,15,17],same:[0,10],save:[0,17],save_timeseries_to_csv:17,sc:[2,15],scenario:[16,17],schema:[0,2],scm:6,script:[6,14,15],sdk:[1,2,3,4,8,10,15,16,17],search1:12,search2:12,search:[0,4,5,9,10,17,18],search_for_timeseries_attribut:[0,2,17],search_match:17,search_queri:[0,10,17],section:[2,5,10,17],secur:[0,1,2,3,15,18],see:[6,10,12,18],select:6,self_signed_certif:[2,15],send:[0,1,2,8],sensibl:2,sensit:2,sensor:9,sent:[8,17],separ:[4,6],sequenc:[4,9],sequenti:[0,2,8],seri:[0,2,4,7,9,10,11],serial:[0,8],server:[0,1,2,5,6,7,8,15,16,17,18],server_config:[2,15],server_kerberos_token:0,servic:[0,2,3,15],service_princip:0,session:[0,2,8,10,14,17,18],session_id:0,set:[0,3,6,10,11,12,14,17,18],setup:[5,14,17,18],sever:[0,10,16],share:5,shell:6,ship:15,should:[0,2,3,6,12,14,15],show:[0,1,2,8,10,14,15,17],show_plot:17,side:0,sight:1,signal:0,signal_final_response_receiv:0,simplethermaltestmodel:2,simplethermaltestresourcecatalog:2,sinc:16,singl:[10,12],size:16,sme:[6,14,18],so:[2,6,9,15],socket:0,softwar:[0,4,7],some:[0,2,3,4,5,6,9,11,12,14,15,16,17],some_python_packag:6,somepowerplantchimney2:2,someth:[0,9,11],sourc:[0,6,10],special:16,specif:[6,9,10,11,12,17],specifi:[0,2,10,12,15],sphinx_copybutton:15,spn:[0,1],squar:12,src:[3,6],ssl:3,ssl_error_ssl:5,ssl_transport_secur:3,staircas:0,staircasestartofstep:0,standard:[0,6],start:[0,2,8,9,10,12,14,17,18],start_and_end_sess:[0,2,8],start_object_guid:[0,2,17],start_object_path:[0,2],start_tim:[0,2,10,17],statement:0,statist:0,statistical_funct:0,statisticalfunct:[0,10],statisticalfunctionsasync:[0,10],statu:[0,9,10],step:[0,5,6,12,16],still:0,storag:6,store:[11,16],storfossdammen:9,str:[0,2,10],stream:0,string:[2,10,15],structur:12,subsequ:[0,1],subset:[2,15],success:[1,4,9],successfulli:[1,2],suffic:6,suffix:12,suggest:[3,6],sum:[0,2,9,10],sumi:[0,10],suppli:17,support:[0,1,6,14,16],sure:[1,2],symbol:10,synchron:[1,2],syntax:[2,4,5,9],system:[1,6,7,9],t:[6,18],tabl:[0,2],tailor:17,take:[1,8,12],target:0,task:[0,2,4,8,9,17],tekicc_st:17,templat:11,temporari:10,termin:6,test:[4,5,6,17,18],test_aio_connect:0,test_async_connection_get_user_ident:0,test_async_connection_revoke_access_token:0,test_async_get_vers:0,test_auth_metadata_plugin_obtains_correctly_new_token_after_delet:0,test_auth_metadata_plugin_obtains_valid_token_in_init:0,test_authent:0,test_can_connect_to_existing_sess:0,test_can_create_empty_timeseri:[0,2,15],test_can_create_timeserie_from_existing_data:0,test_can_serialize_and_deserialize_write_timeserie_request:0,test_commit:0,test_connect:0,test_connection_get_user_ident:0,test_connection_revoke_access_token:0,test_delete_access_token:0,test_exampl:0,test_get_timeseri:0,test_get_timeseries_async:0,test_get_vers:0,test_history_get_all_forecast:0,test_history_get_forecast:0,test_history_get_ts_as_of_tim:0,test_history_get_ts_historical_vers:0,test_is_grpc_respond:0,test_is_valid_token_returns_false_for_deleted_access_token:0,test_open_and_close_sess:0,test_read_timeseries_attribut:0,test_read_timeseries_attribute_async:0,test_read_timeseries_point:0,test_read_timeseries_points_async:0,test_read_timeseries_points_without_specifying_timeseries_should_throw:0,test_read_transformed_timeseries_point:0,test_read_transformed_timeseries_points_with_uuid:0,test_rollback:0,test_run_example_script:0,test_search_timeseries_attribut:0,test_search_timeseries_attribute_async:0,test_sess:0,test_sessions_using_async_contextmanag:0,test_sessions_using_contextmanag:0,test_statistical_sum:0,test_timeseri:[0,2,15],test_update_timeseries_attribute_with_timeseriescalcul:0,test_update_timeseries_attribute_with_timeseriescalculation_async:0,test_update_timeseries_attribute_with_timeseriesrefer:0,test_update_timeseries_attribute_with_timeseriesreference_async:0,test_update_timeseries_entri:0,test_update_timeseries_entry_async:0,test_util:[2,15],test_write_timeseries_point:0,test_write_timeseries_points_async:0,test_write_timeseries_points_using_timskey_async:0,text:12,than:[0,2,10,11],thei:[0,6,9,12,15],them:[0,2,5,6,11,15,16],theme:9,thermalcompon:2,thi:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],thing:3,think:5,those:9,thrown:0,time:[0,1,2,4,5,7,8,9,10,11,17],timeseri:[0,5,10,14,17,18],timeseries_attribut:2,timeseries_full_nam:2,timeseries_id:2,timeseries_oper:0,timeseries_read:2,timeseriesattribut:0,timeseriesentri:0,timeseriesentryid:0,timestamp:[0,2,16],timezon:[0,2,10],timskei:[0,2,10,18],tl:[1,2,3,18],to_panda:[2,17],todo:14,token:[0,2],tool:[4,6,15],toward:[1,18],tracker:[3,5],transform:[0,2,9,18],transform_paramet:2,traver:2,travers:[4,9],treat:2,tree:9,troubl:5,tsi:3,tsrawatt:2,turn:3,two:[0,1,2,6,8,10],type:[0,2,10,11,16,17],typeerror:[0,10],uint32:[0,2],uncom:[2,15],underli:11,understand:7,union:12,unit:[2,9,11,16],unit_of_measur:2,unittest:[2,15],univers:0,unix:[2,16],unknown:0,unless:6,unprotect:10,unspecifi:0,until:1,up:[0,3,6,14,17],updat:[0,18],update_timeseries_attribut:0,update_timeseries_resource_info:[0,18],upn:1,us:[0,1,3,4,5,6,7,8,9,10,12,14,15,16,18],use_cas:17,use_case_1:17,use_case_nam:17,usecas:18,user:[0,1,2,5,15,18],user_ident:[1,2],user_princip:0,userident:0,usr:[0,10],usual:1,utc:[0,2,16],utc_tim:[0,2],uuid:[0,2,10,17],uuid_id:[0,2,10,17],v1alpha:0,valid:[0,1,10,11],valu:[0,2,9,10,11,16],variabl:[10,14],variou:18,venv:4,verbos:[2,15],verifi:[0,3,15],version:[0,1,4,6,8,10,14],version_info:2,versioninfo:0,view:6,virtual:[4,6,14],visual:[17,18],volu:[1,2,3,5,6,8,10,12,14,15],vv:[2,15],wa:0,wai:[0,2,6,8,14],wait:[0,8],walk:12,want:[0,1,2,6,9,14,17],warn:15,water:9,we:[1,2,6,14,17],week:0,were:17,what:[2,5,15],when:[0,1,2,3,6,10,12,18],where:[6,9,12],which:[0,2,8,9,10,11,12,14,15,17],whose:12,wide:9,win:0,window:[1,6],winkerbero:[1,2,15],within:[0,10,12,14],without:[0,1,2,3,15],wizard:6,won:18,work:[1,2,4,6,7,10,17,18],would:[1,2,15],wrapper:10,write:[0,4,5,6,15,18],write_timeseries_point:[0,2],write_timeseries_points_async:0,written:[0,2,15],wrong:5,wrong_version_numb:3,xml:[2,15],year:0,yet:[0,2,8],yield:0,you:[0,1,2,3,5,6,12,14,15,17,18],your:[1,2,3,5,6,14,15,17],your_python_script:6,zone:0},titles:["API documentation","Authentication","Examples","Frequently Asked Questions","Glossary","Welcome to Mesh Python SDK","Installation","An introduction to Mesh","Mesh client","Mesh concepts","Mesh functions","Attributes","Mesh search language","Mesh server","Quickstart guide","Tests","Time series","Use cases","Versions"],titleterms:{"0":18,"2":18,"3":18,"case":17,"do":3,"function":[10,17],"new":18,The:17,add:17,aio:0,alpha:18,am:3,an:7,api:0,ask:3,asynchron:2,attribut:[2,11],authent:1,author:2,bug:3,calc:0,call:14,chang:18,client:8,combin:12,compat:18,concept:9,configur:[3,17],connect:[2,3,8],criteria:12,definit:10,depend:[6,17],develop:6,document:0,edit:17,environ:6,error:3,exampl:[0,1,2],fail:3,featur:[3,5,18],first:14,found:3,frequent:3,get:[2,3,5,17],git:6,github:6,glossari:4,grpc:3,guid:14,have:3,help:[3,5],helper:17,histori:10,i:3,indic:5,instal:[6,14,17,18],instruct:18,introduct:7,issu:18,known:18,languag:12,mesh:[0,1,3,5,6,7,8,9,10,12,13,14,18],more:3,multipl:12,need:3,next:14,one:3,oper:12,other:3,panda:2,prefer:17,prepar:15,prerequisit:[5,14],princip:1,pycharm:6,python:[5,6,18],queri:12,question:3,quickstart:[2,14],ran:3,read:2,recommend:6,refer:5,request:3,requir:1,run:[2,15,17],sdk:[5,6,18],search:[2,12],seri:16,server:[3,13,14],servic:1,setup:6,ssl_error_ssl:3,start:5,statist:10,step:14,syntax:12,tabl:5,test:[0,2,3,15],them:3,think:3,time:16,timeseri:2,token:1,transform:10,travers:12,us:[2,17],usag:1,user:6,version:[2,5,18],volu:0,welcom:5,what:3,write:2,wrong:3}})