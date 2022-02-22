Search.setIndex({docnames:["api","authentication","concepts","examples","faq","glossary","index","installation","news","quickstart","tests"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api.rst","authentication.rst","concepts.rst","examples.rst","faq.rst","glossary.rst","index.rst","installation.rst","news.rst","quickstart.rst","tests.rst"],objects:{"volue.mesh":[[0,1,1,"","Authentication"],[0,1,1,"","Connection"],[0,1,1,"","Credentials"],[0,1,1,"","Timeseries"],[0,0,0,"-","aio"],[0,0,0,"-","examples"],[0,0,0,"-","tests"]],"volue.mesh.Authentication":[[0,1,1,"","KerberosTokenIterator"],[0,1,1,"","Parameters"],[0,2,1,"","delete_access_token"],[0,2,1,"","get_token"],[0,2,1,"","is_token_valid"]],"volue.mesh.Authentication.KerberosTokenIterator":[[0,2,1,"","process_response"],[0,2,1,"","signal_final_response_received"]],"volue.mesh.Authentication.Parameters":[[0,3,1,"","service_principal"],[0,3,1,"","user_principal"]],"volue.mesh.Connection":[[0,1,1,"","Session"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.Connection.Session":[[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.Timeseries":[[0,1,1,"","Curve"],[0,1,1,"","PointFlags"],[0,1,1,"","Resolution"],[0,4,1,"","is_calculation_expression_result"],[0,4,1,"","number_of_points"],[0,3,1,"","schema"]],"volue.mesh.Timeseries.Curve":[[0,3,1,"","PIECEWISELINEAR"],[0,3,1,"","STAIRCASE"],[0,3,1,"","STAIRCASESTARTOFSTEP"],[0,3,1,"","UNKNOWN"]],"volue.mesh.Timeseries.PointFlags":[[0,3,1,"","MISSING"],[0,3,1,"","NOT_OK"],[0,3,1,"","OK"]],"volue.mesh.Timeseries.Resolution":[[0,3,1,"","BREAKPOINT"],[0,3,1,"","DAY"],[0,3,1,"","HOUR"],[0,3,1,"","MIN15"],[0,3,1,"","MONTH"],[0,3,1,"","UNSPECIFIED"],[0,3,1,"","WEEK"],[0,3,1,"","YEAR"]],"volue.mesh.aio":[[0,1,1,"","Connection"]],"volue.mesh.aio.Connection":[[0,1,1,"","Session"],[0,2,1,"","connect_to_session"],[0,2,1,"","create_session"],[0,2,1,"","get_user_identity"],[0,2,1,"","get_version"],[0,2,1,"","revoke_access_token"]],"volue.mesh.aio.Connection.Session":[[0,2,1,"","close"],[0,2,1,"","commit"],[0,2,1,"","get_timeseries_attribute"],[0,2,1,"","get_timeseries_resource_info"],[0,2,1,"","open"],[0,2,1,"","read_timeseries_points"],[0,2,1,"","rollback"],[0,2,1,"","search_for_timeseries_attribute"],[0,2,1,"","update_timeseries_attribute"],[0,2,1,"","update_timeseries_resource_info"],[0,2,1,"","write_timeseries_points"]],"volue.mesh.examples":[[0,0,0,"-","connect_asynchronously"],[0,0,0,"-","connect_synchronously"],[0,0,0,"-","get_version"],[0,0,0,"-","quickstart"],[0,0,0,"-","read_timeseries_points"],[0,0,0,"-","read_timeseries_points_async"],[0,0,0,"-","timeseries_operations"],[0,0,0,"-","write_timeseries_points"],[0,0,0,"-","write_timeseries_points_async"]],"volue.mesh.examples.connect_asynchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.connect_synchronously":[[0,5,1,"","get_version"],[0,5,1,"","main"],[0,5,1,"","start_and_end_session"]],"volue.mesh.examples.get_version":[[0,5,1,"","main"]],"volue.mesh.examples.quickstart":[[0,5,1,"","main"]],"volue.mesh.examples.read_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points"]],"volue.mesh.examples.read_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","read_timeseries_points_async"]],"volue.mesh.examples.timeseries_operations":[[0,5,1,"","main"]],"volue.mesh.examples.write_timeseries_points":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.examples.write_timeseries_points_async":[[0,5,1,"","main"],[0,5,1,"","write_timeseries_points"]],"volue.mesh.tests":[[0,0,0,"-","test_aio_connection"],[0,0,0,"-","test_authentication"],[0,0,0,"-","test_connection"],[0,0,0,"-","test_examples"],[0,0,0,"-","test_session"],[0,0,0,"-","test_timeseries"]],"volue.mesh.tests.test_aio_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_get_timeseries_async"],[0,5,1,"","test_read_history_timeseries_points"],[0,5,1,"","test_read_timeseries_attribute_async"],[0,5,1,"","test_read_timeseries_points_async"],[0,5,1,"","test_read_timeseries_points_with_specifying_both_history_and_transform_parameters_should_throw"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute_async"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation_async"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference_async"],[0,5,1,"","test_update_timeseries_entry_async"],[0,5,1,"","test_write_timeseries_points_async"],[0,5,1,"","test_write_timeseries_points_using_timskey_async"]],"volue.mesh.tests.test_authentication":[[0,5,1,"","aconnection"],[0,5,1,"","auth_metadata_plugin"],[0,5,1,"","connection"],[0,5,1,"","test_async_connection_get_user_identity"],[0,5,1,"","test_async_connection_revoke_access_token"],[0,5,1,"","test_auth_metadata_plugin_obtains_correctly_new_token_after_delete"],[0,5,1,"","test_auth_metadata_plugin_obtains_valid_token_in_init"],[0,5,1,"","test_connection_get_user_identity"],[0,5,1,"","test_connection_revoke_access_token"],[0,5,1,"","test_delete_access_token"],[0,5,1,"","test_is_valid_token_returns_false_for_deleted_access_token"]],"volue.mesh.tests.test_connection":[[0,5,1,"","test_commit"],[0,5,1,"","test_get_timeseries"],[0,5,1,"","test_read_history_timeseries_points"],[0,5,1,"","test_read_timeseries_attribute"],[0,5,1,"","test_read_timeseries_points"],[0,5,1,"","test_read_timeseries_points_with_specifying_both_history_and_transform_parameters_should_throw"],[0,5,1,"","test_read_timeseries_points_without_specifying_timeseries_should_throw"],[0,5,1,"","test_read_transformed_timeseries_points"],[0,5,1,"","test_read_transformed_timeseries_points_with_uuid"],[0,5,1,"","test_rollback"],[0,5,1,"","test_search_timeseries_attribute"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriescalculation"],[0,5,1,"","test_update_timeseries_attribute_with_timeseriesreference"],[0,5,1,"","test_update_timeseries_entry"],[0,5,1,"","test_write_timeseries_points"]],"volue.mesh.tests.test_examples":[[0,5,1,"","test_is_grpc_responding"],[0,5,1,"","test_run_example_scripts"]],"volue.mesh.tests.test_session":[[0,5,1,"","test_async_get_version"],[0,5,1,"","test_can_connect_to_existing_session"],[0,5,1,"","test_get_version"],[0,5,1,"","test_open_and_close_session"],[0,5,1,"","test_sessions_using_async_contextmanager"],[0,5,1,"","test_sessions_using_contextmanager"]],"volue.mesh.tests.test_timeseries":[[0,5,1,"","test_can_create_empty_timeserie"],[0,5,1,"","test_can_create_timeserie_from_existing_data"],[0,5,1,"","test_can_serialize_and_deserialize_write_timeserie_request"]],volue:[[0,0,0,"-","mesh"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","property","Python property"],"5":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:property","5":"py:function"},terms:{"0":[0,2,3,6,9,10],"0000":3,"000000000000":3,"00000003":3,"0003":3,"09":4,"1":[0,1,2,3,6,7,8,9,10],"10":[2,3],"1000":3,"100000f7":4,"1073741824":0,"115":8,"116":8,"12":[2,3],"120":8,"122":8,"1468":4,"2":[0,2,3,6],"2016":[2,3],"2078":[1,3,10],"24":[2,3],"26":4,"29912":4,"3":[0,2,3,6,7,8,9,10],"4":[0,2,3,10],"5":[0,2,3],"50051":[3,9,10],"59":4,"6":[0,3],"667000000":4,"67108864":0,"7":[0,6,7,8,9],"72":[2,3],"8":[0,3,6,7,8,9],"9":[6,7,8,9],"99":9,"byte":0,"case":[0,1,2,4,8,9,10],"class":0,"default":9,"do":[2,3,6,10],"final":0,"function":[0,1,2,3,4,5,6,7,8,9,10],"import":[1,2,3,9,10],"int":[0,2,3],"long":2,"new":[0,1,6,7],"return":[0,2,3],"throw":0,"true":[1,3,4],"try":[0,2,3,4,6],"while":2,A:[2,3,5],For:[1,2,4,7,9],If:[0,1,3,4,6,9,10],In:[0,4,7,9,10],Is:4,It:[1,7,9],No:[0,2,3],OR:3,Or:[1,3,7],The:[0,1,2,3,6,7,9,10],These:[3,7,10],To:[1,6,7,10],_:2,__main__:[1,2,3,9,10],__name__:[1,2,3,9,10],_authent:0,_connect:0,_get_connection_info:[1,2,3,9],_timeseri:0,abl:10,about:8,abov:4,accept:8,access:[0,1,3],account:[1,3,10],aconnect:[0,1,3],acquir:[0,2],action:1,activ:[1,7,8],ad:[0,1,3,7,10],addit:[1,7],address:[0,1,2,3,4,9,10],after:[0,1,2,7],aio:[1,2,3,6],aliv:0,all:[0,1,2,3,4,7,9,10],allevi:2,allow:10,alpha:6,also:[1,7],am:6,an:[0,2,3,9],ani:[0,1,2,3,4],anoth:2,anyon:1,apach:[2,6,7],api:[1,5,6],append:[2,3],applic:5,ar:[0,1,2,3,4,6,7,9,10],arbitrari:7,argument:0,arrai:[2,3],arrow:[2,3,6,7],arrow_t:[2,3],ask:[6,9],assum:[7,9],async:[0,2,3,6],asyncconnect:[0,1,3],asynchron:[0,1,6],asyncio:[0,1,2,3,4,5,6,7,8,9,10],asynio:0,attribut:[0,2,3],auth_metadata_plugin:0,authent:[0,3,4,6,8,10],authenticatekerbero:[0,1],authentication_paramet:[0,1,3],author:[0,1,6],automat:[1,8],avail:[7,10],await:[2,3,6],b:[2,3],back:2,base:[3,4],basic:6,bat:7,becaus:[0,1],been:2,behav:[0,8],believ:4,below:7,between:0,bin:7,binari:7,board:4,bool:0,both:[0,2,3,8],breakpoint:0,bug:[6,8],build:7,build_dat:9,cach:10,calc:[0,2,3],calcul:0,call:[0,1,6,7],can:[0,1,2,3,4,7,9,10],cancel:0,caus:4,cc:4,cd:7,center:1,certain:0,challeng:0,chang:[0,2,3,4,6,7,9,10],channel_credenti:0,channelcredenti:0,charact:[1,3,10],check:[0,2,3,4,9],chimney2timeseriesraw:3,clean:0,client:[0,1,2,3,4,6,7],clone:7,close:[0,2,3,9],cmd:[3,10],code:[0,3,4,9],collect:5,com:[1,3,7,8,9,10],combin:0,come:7,command:7,commit:[0,3,8,9],common:[2,3],commun:[1,2,3,6,9],compani:[1,3,10],companyad:[1,3,10],compat:6,complet:[0,2],compound_stmt:0,concept:[0,6,7],concurr:[0,2,3],confidenti:4,configur:[0,1,3,6,9],confirm:1,connect:[0,1,2,6,8,9,10],connect_asynchron:0,connect_synchron:0,connect_to_sess:0,consist:1,consult:[1,4,9],consum:2,contact:[1,4,9],contain:[0,3],context:0,contextmanag:0,convert:[0,1,2,3,10],copi:2,core:[0,4],core_pb2:0,core_pb2_grpc:0,coroutin:[0,1,2,3,4,5,6,7,8,9,10],correct:[1,4],correctli:[0,4],could:[0,1,2,3,4,5,6,7,8,9,10],creat:[0,1,2,3,7,8,9],create_sess:[0,2,3,9],credenti:0,critic:8,current:[0,1,6],curv:[0,2,3],curve_typ:[2,3],custom:4,dai:[0,2,3],data:[0,2,3,9,10],databas:[2,3,5,10],datamodel:0,datetim:[0,2,3],db:[5,10],de:0,def:[1,2,3,9,10],defaultserverconfig:[3,10],defin:3,delet:0,delete_access_token:0,demonstr:[2,4],depend:[0,1,2,6],deprec:[0,1,2,3,4,5,6,7,8,9,10],depth:7,detail:[0,4],dev:[2,3],develop:[5,6,7],differ:[7,9],directori:[1,7,8],discard:[0,2,3],discuss:4,displai:8,distribut:1,doc:[0,2],document:[6,7,8,10],doe:[0,1,4,8],done:[0,1,2,3],doubl:0,drop:7,due:7,durat:0,e0903:4,e:[0,1,2,3,7,10],each:1,earlier:7,either:[0,4,8,9],els:1,empti:0,enabl:[1,2,3,4,6,9],enablekerbero:[1,3],enabletl:[1,3,4],encrypt:1,end:[0,2,3],end_tim:[0,2,3],energi:[0,6],enough:[1,3,10],entri:[0,2,3],enumer:0,environ:[6,9],error:[0,6],ever:0,everi:1,everyth:9,exampl:[2,4,6,7,8,9,10],examplecompani:[1,3,10],except:[0,2,3,10],exist:0,exit:0,expect:[0,8],expected_number_of_point:0,expir:1,expos:1,express:[0,2,3],extern:7,f:[2,3,9],fail:[6,10],fals:[0,3,10],fatal:4,featur:[0,1],field:0,file:9,find:[0,1,2,3],finish:1,first:[2,3,4,6,7,8],fit:[3,10],flag:[0,2,3],float64:[2,3],flow:0,follow:[0,2,3,4,8,9,10],forc:8,format:[0,1,2,3,10],found:[3,6,7,10],frequent:[6,9],from:[0,1,2,3,6,8,9,10],from_arrai:[2,3],full:[3,8],full_nam:[0,2,3],full_name_timeseri:3,full_vers:[3,9],further:[2,3],g:[0,1,3,7,10],gather:[2,3],gener:[0,3,4,7,10],get:[0,1,2,8,9],get_event_loop:[1,3],get_timeseries_attribut:[0,8],get_timeseries_resource_info:0,get_token:0,get_user_ident:[0,1,3],get_vers:[0,2,3,7,9],getuserident:[1,3],getvers:1,git:[7,8,9],github:[7,8,9],given:[0,2,3],glossari:6,go:7,greater:[2,3],group:10,grpc:[0,1,2,3,6,7,9,10],gsserror:0,guid:[0,3,6,8],ha:[0,1,2],handshak:4,have:[0,1,3,6,9],head:6,help:7,here:[6,7,9],histori:0,hoc:0,host:[0,1,3,4,10],hostnam:[1,3,10],hour:[0,1,2,3],how:[0,1,2,3,6,10],html:[0,2],http:[0,2,7,8,9],i:[2,3,6],id:[2,3],id_timeseri:3,ident:[0,1],identifi:3,implement:2,includ:[2,4],index:6,indic:[2,3,10],individu:[3,10],info:[1,3],inform:[0,4,7,9,10],ini_opt:10,insecur:8,insid:0,instal:[3,5,6,10],instanti:1,instruct:[4,6,10],intend:[0,8],intens:2,interfac:5,interv:[0,3],invalid:0,is_calculation_expression_result:0,is_token_valid:0,issu:[4,6],iter:0,its:[0,9,10],junitxml:[3,10],just:1,kdc:1,keep:0,kei:1,kerbero:[0,1,3,8],kerberos_service_principal_nam:[3,10],kerberostokeniter:0,kit:5,known:6,languag:0,larg:2,last:[2,3],learn:6,left:0,len:[2,3],let:[2,3,9],lib:0,librari:[0,2,6,9],like:[0,4,9],line:1,linux:7,list:[0,4],local:[0,9],localhost:[3,10],localsystem:[1,3,10],log:[1,10],longer:[0,1,3],m:[3,7,8,9,10],mac:7,machin:9,made:[0,8,9],mai:[0,1,2,7],main:[0,1,2,3,9,10],maintain:7,major:8,make:[1,2,3,7],manag:[0,7],mark:10,marker:10,mean:[0,2],meant:0,measur:[2,3],member:0,memori:[2,6],mesh:[2,3,10],mesh_server_vers:[3,9],mesh_servic:0,mesh_v2:8,meshservicestub:0,metadata:8,method:[0,1,2,3],might:[4,6,10],millisecond:[2,3],min15:0,minor:8,miss:0,mkdir:7,model:[0,2,3,8],model_nam:[2,3],modul:[0,6],month:0,more:[0,2,6,9,10],move:2,ms:[0,2,3],much:4,multipl:[4,7],must:[1,2,3],my:7,myproject:7,name:[1,2,3,8,9,10],namespac:0,need:[0,1,6,7,10],neither:4,network:[2,4,9],networkservic:[1,3,10],new_:0,new_curve_typ:0,new_local_express:0,new_path:0,new_timeseries_entry_id:0,new_unit_of_measur:0,newli:0,next:[0,6],nimbu:8,non:9,none:0,not_ok:0,note:[0,1,3,10],noteworthi:6,now:[2,3,7,9],number:[0,2,3],number_of_point:[0,2,3],numpi:2,object:[0,1,8],obtain:[0,1],offici:7,ok:[0,2,3],old:0,one:[0,2,5,6],onli:[0,1,2,3],open:[0,2,3,9],openssl_intern:4,oper:[2,3],optimis:6,option:[0,1,2,3,9,10],oracl:8,org:[0,2],organ:[2,3],other:[0,2,6],our:[2,3,6,7],out:[1,9],output:[2,3,9,10],over:[2,6],pa:[2,3],packag:[0,2,3,5,7],panda:[0,2,6,10],pandas_seri:[2,3],param:0,paramet:[0,1,2,3],pass:10,path:[0,2,3,7,8],perform:[1,2],physic:8,pick:[2,3],piecewiselinear:0,ping:4,pip:[6,8,9,10],pleas:[1,4,9],poetri:7,point:[0,2,3,8],pointflag:[0,2,3],port:[0,1,2,3,4,9,10],possibl:[0,4],powela:[7,8,9],prefer:4,prepar:[0,6],press:4,primari:2,princip:[3,6,10],print:[1,2,3,9],problem:[2,4,9],process:[0,1,2,3],process_respons:0,program:5,project:[7,9],properti:0,proto:0,protobuf:7,protocol:[1,8],prove:1,provid:[0,1,2,3,7,10],purpos:7,py:[0,1,7,9],pyarg:[3,10],pyarrow:[0,2,3],pytest:[0,1,2,3,4,5,6,7,8,9,10],python3:[0,7],python:[0,1,2,3,4,9,10],queri:[0,2,3,8],question:[6,9],quick:[7,9],quickest:[0,3,9],quickstart:[0,6],quit:2,r:[1,3,10],ra:[3,10],rais:0,ran:[6,7],rang:[2,3],re:[6,7],read:[0,2,4,6,8,10],read_timeseries_point:[0,2,3],read_timeseries_points_async:[0,3],reason:1,receiv:[0,1,3],recommend:[7,9],refer:[0,1,7,9],referenc:7,regard:[4,9],regist:[1,3,10],reinstal:8,remot:[3,9],report:[3,4,6,10],repositori:7,request:[0,1,2,3,6,9],requir:[0,2,3,4,5,6,7,8,9,10],reset:0,resolut:[0,2,3],resolv:4,resourc:[3,6],resources_pb2:0,respond:0,respons:[0,2],result:[0,1,3,8],retriev:[0,2],revok:[0,1,3],revoke_access_token:[0,1,3],revokeaccesstoken:0,rfc:[1,3,10],right:9,rollback:[0,2,3,8],routin:4,rpcerror:[0,2,3],run:[0,1,2,4,6,7,8,9],run_until_complet:[1,3],runtim:7,runtimeerror:0,s:[0,1,4,6,7],same:0,sc:[3,10],scenario:2,schema:[0,2,3],script:[7,9,10],sdk:[1,2,3,4,5,7,10],search:[0,2,3,8],search_for_timeseries_attribut:[0,2,3],section:[3,6],secur:[0,1,3,4,8,10],secure_connect:[0,1,2,3,9,10],see:[7,8,9],send:[0,1,2,3],sensibl:3,sent:2,separ:7,sequenti:[0,2,3],serial:[0,2],server:[0,1,2,3,6,8,10],server_config:[3,10],server_kerberos_token:0,servic:[0,3,4,6,10],service_princip:0,session:[0,2,3,8,9],session_id:0,set:[0,4,9],setup:9,sever:[0,2],share:6,shell:7,ship:10,should:[0,3,4,7,9,10],show:[0,1,2,3,9,10],side:0,sight:1,signal:0,signal_final_response_receiv:0,simplethermaltestmodel:[2,3],simplethermaltestresourcecatalog:3,size:2,sme:[7,8,9],so:7,socket:0,softwar:[0,5],some:[0,2,3,4,6,9,10],somepowerplantchimney2:[2,3],someth:0,sourc:[0,6],specif:7,specifi:[0,3,10],sphinx_copybutton:10,spn:[0,1],src:[4,7],ssl:4,ssl_error_ssl:6,ssl_transport_secur:4,staircas:0,staircasestartofstep:0,standard:7,start:[0,2,3,8,9],start_and_end_sess:[0,2,3],start_object_guid:0,start_object_path:[0,2,3],start_tim:[0,2,3],statement:0,step:[0,6,7],still:0,store:2,str:[0,2,3],stream:0,subsequ:[0,1],subset:[3,10],success:1,successfulli:[1,3],suggest:4,sum:[2,3],support:[0,1,2,7,9],sure:[1,2,3],synchron:[1,3],syntax:6,system:1,t:8,tabl:[0,2,3],take:[1,2],target:0,task:[0,2,3],test:[6,7,8],test_aio_connect:0,test_async_connection_get_user_ident:0,test_async_connection_revoke_access_token:0,test_async_get_vers:0,test_auth_metadata_plugin_obtains_correctly_new_token_after_delet:0,test_auth_metadata_plugin_obtains_valid_token_in_init:0,test_authent:0,test_can_connect_to_existing_sess:0,test_can_create_empty_timeseri:[0,3,10],test_can_create_timeserie_from_existing_data:0,test_can_serialize_and_deserialize_write_timeserie_request:0,test_commit:0,test_connect:0,test_connection_get_user_ident:0,test_connection_revoke_access_token:0,test_delete_access_token:0,test_exampl:0,test_get_timeseri:0,test_get_timeseries_async:0,test_get_vers:0,test_is_grpc_respond:0,test_is_valid_token_returns_false_for_deleted_access_token:0,test_open_and_close_sess:0,test_read_history_timeseries_point:0,test_read_timeseries_attribut:0,test_read_timeseries_attribute_async:0,test_read_timeseries_point:0,test_read_timeseries_points_async:0,test_read_timeseries_points_with_specifying_both_history_and_transform_parameters_should_throw:0,test_read_timeseries_points_without_specifying_timeseries_should_throw:0,test_read_transformed_timeseries_point:0,test_read_transformed_timeseries_points_with_uuid:0,test_rollback:0,test_run_example_script:0,test_search_timeseries_attribut:0,test_search_timeseries_attribute_async:0,test_sess:0,test_sessions_using_async_contextmanag:0,test_sessions_using_contextmanag:0,test_timeseri:[0,3,10],test_update_timeseries_attribute_with_timeseriescalcul:0,test_update_timeseries_attribute_with_timeseriescalculation_async:0,test_update_timeseries_attribute_with_timeseriesrefer:0,test_update_timeseries_attribute_with_timeseriesreference_async:0,test_update_timeseries_entri:0,test_update_timeseries_entry_async:0,test_util:[3,10],test_write_timeseries_point:0,test_write_timeseries_points_async:0,test_write_timeseries_points_using_timskey_async:0,than:[2,3],thei:[0,7,10],them:[0,2,3,6],thermalcompon:[2,3],thi:[0,1,2,3,4,5,6,7,8,9,10],thing:4,think:6,those:7,thrown:0,time:[0,1,2,3,6],timeseri:[0,2,6,8,9],timeseries_attribut:[2,3],timeseries_full_nam:3,timeseries_id:3,timeseries_oper:0,timeseries_read:[2,3],timeseriesattribut:0,timeseriesentri:0,timeseriesentryid:0,timestamp:[0,2,3],timezon:[0,2,3],timskei:[0,3,8],tl:[1,3,4],to_panda:[2,3],todo:9,token:[0,3,6],tool:[5,10],toward:[1,8],tracker:[4,6],transform:[0,2,3],transform_paramet:[2,3],treat:[2,3],troubl:6,tsi:4,tsrawatt:[2,3],turn:4,two:[0,1,2,3],type:[0,2,3],typeerror:0,uint32:[0,2,3],uncom:[3,10],under:7,unit:[2,3],unit_of_measur:[2,3],unittest:[3,10],unix:[2,3],unknown:0,unless:7,unspecifi:0,until:1,up:[0,4,7,9],updat:[0,8],update_timeseries_attribut:0,update_timeseries_resource_info:[0,8],upn:1,us:[0,1,2,4,6,8,9,10],usag:6,user:[0,1,3,10],user_ident:[1,3],user_princip:0,userident:0,usr:0,usual:1,utc:[2,3],utc_tim:[0,2,3],uuid:[0,3],uuid_id:[0,2,3],v1alpha:0,valid:[0,1],valu:[0,2,3],variabl:9,venv:7,verbos:[3,10],verifi:[0,4,10],version:[0,1,2,6,7,9],version_info:3,versioninfo:0,virtual:[6,9],visual:8,volu:[1,2,3,4,6,7,9,10],vv:[3,10],wa:0,wai:[0,2,3,7,9],wait:[0,2],want:[0,1,3,7,9],warn:10,we:[1,3,9],week:0,what:[6,10],when:[0,1,3,4,7,8],which:[0,2,3,9,10],win:0,window:[1,7],winkerbero:[1,3,10],within:9,without:[0,1,3,4,10],won:8,work:[1,2,3,7,8],would:[1,3,10],write:[0,2,6,8,10],write_timeseries_point:[0,2,3],write_timeseries_points_async:0,written:[0,2,3,10],wrong:6,wrong_version_numb:4,xml:[3,10],year:0,yet:[0,2,3],yield:0,you:[0,1,3,4,6,7,9,10],your:[1,3,4,6,7,9,10]},titles:["API documentation","Authentication","Concepts","Examples","Frequently Asked Questions","Glossary","Welcome to Mesh Python SDK","Installation","News","Quickstart guide","Tests"],titleterms:{"0":8,"2":8,"do":4,"new":8,aio:0,alpha:8,am:4,api:0,ask:4,asynchron:3,authent:1,author:3,basic:2,bug:4,call:9,chang:8,compat:8,concept:2,configur:4,connect:[3,4],depend:7,document:0,environ:7,error:4,exampl:[0,1,3],fail:4,featur:[4,6,8],first:9,found:4,frequent:4,from:7,get:[3,4,6],glossari:5,grpc:4,guid:9,have:4,help:[4,6],i:4,indic:6,instal:[7,8,9],instruct:8,issu:8,known:8,librari:7,mesh:[0,1,4,6,7,8,9],more:4,need:4,next:9,one:4,other:4,panda:3,pip:7,prepar:10,prerequisit:[6,9],princip:1,python:[6,7,8],question:4,quickstart:[3,9],ran:4,read:3,refer:6,request:4,requir:1,run:[3,10],sdk:[6,8],server:[4,9],servic:1,sourc:7,ssl_error_ssl:4,start:6,step:9,tabl:6,test:[0,3,4,10],them:4,think:4,timeseri:3,token:1,us:[3,7],usag:1,version:[3,8],virtual:7,volu:0,welcom:6,what:4,write:3,wrong:4}})