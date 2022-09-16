Search.setIndex({docnames:["api","authentication","examples","faq","glossary","index","installation","introduction_to_mesh","mesh_client","mesh_concepts","mesh_functions","mesh_modelling","mesh_rating_curve","mesh_relations","mesh_search","mesh_server","mesh_session","mesh_xy_sets","quickstart","tests","timeseries","usecases","versions"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["api.rst","authentication.rst","examples.rst","faq.rst","glossary.rst","index.rst","installation.rst","introduction_to_mesh.rst","mesh_client.rst","mesh_concepts.rst","mesh_functions.rst","mesh_modelling.rst","mesh_rating_curve.rst","mesh_relations.rst","mesh_search.rst","mesh_server.rst","mesh_session.rst","mesh_xy_sets.rst","quickstart.rst","tests.rst","timeseries.rst","usecases.rst","versions.rst"],objects:{"volue.mesh":[[0,1,1,"","AttributeBase"],[0,1,1,"","AttributesFilter"],[0,1,1,"","Authentication"],[0,1,1,"","Connection"],[0,1,1,"","Credentials"],[0,1,1,"","LinkRelationAttribute"],[0,1,1,"","LinkRelationVersion"],[0,1,1,"","Object"],[0,1,1,"","OwnershipRelationAttribute"],[0,1,1,"","RatingCurveSegment"],[0,1,1,"","RatingCurveVersion"],[0,1,1,"","Timeseries"],[0,1,1,"","TimeseriesAttribute"],[0,1,1,"","TimeseriesResource"],[0,1,1,"","UserIdentity"],[0,1,1,"","VersionInfo"],[0,1,1,"","VersionedLinkRelationAttribute"],[0,1,1,"","XyCurve"],[0,1,1,"","XySet"],[0,0,0,"-","aio"],[0,0,0,"-","calc"]],"volue.mesh.AttributeBase":[[0,1,1,"","AttributeBaseDefinition"]],"volue.mesh.AttributesFilter":[[0,2,1,"","name_mask"],[0,2,1,"","namespace_mask"],[0,2,1,"","return_no_attributes"],[0,2,1,"","tag_mask"]],"volue.mesh.Authentication":[[0,1,1,"","KerberosTokenIterator"],[0,1,1,"","Parameters"],[0,3,1,"","__init__"],[0,3,1,"","delete_access_token"],[0,3,1,"","get_token"],[0,3,1,"","is_token_valid"]],"volue.mesh.Authentication.KerberosTokenIterator":[[0,3,1,"","__init__"],[0,3,1,"","process_response"],[0,3,1,"","signal_final_response_received"]],"volue.mesh.Authentication.Parameters":[[0,2,1,"","service_principal"],[0,2,1,"","user_principal"]],"volue.mesh.Connection":[[0,1,1,"","Session"],[0,3,1,"","connect_to_session"],[0,3,1,"","create_session"],[0,3,1,"","get_user_identity"],[0,3,1,"","get_version"],[0,3,1,"","revoke_access_token"]],"volue.mesh.Connection.Session":[[0,3,1,"","close"],[0,3,1,"","commit"],[0,3,1,"","create_object"],[0,3,1,"","delete_object"],[0,3,1,"","forecast_functions"],[0,3,1,"","get_attribute"],[0,3,1,"","get_object"],[0,3,1,"","get_rating_curve_versions"],[0,3,1,"","get_timeseries_attribute"],[0,3,1,"","get_timeseries_resource_info"],[0,3,1,"","get_xy_sets"],[0,3,1,"","history_functions"],[0,3,1,"","open"],[0,3,1,"","read_timeseries_points"],[0,3,1,"","rollback"],[0,3,1,"","search_for_attributes"],[0,3,1,"","search_for_objects"],[0,3,1,"","search_for_timeseries_attributes"],[0,3,1,"","statistical_functions"],[0,3,1,"","transform_functions"],[0,3,1,"","update_link_relation_attribute"],[0,3,1,"","update_object"],[0,3,1,"","update_rating_curve_versions"],[0,3,1,"","update_simple_attribute"],[0,3,1,"","update_timeseries_attribute"],[0,3,1,"","update_timeseries_resource_info"],[0,3,1,"","update_versioned_link_relation_attribute"],[0,3,1,"","update_xy_sets"],[0,3,1,"","write_timeseries_points"]],"volue.mesh.Credentials":[[0,3,1,"","__init__"]],"volue.mesh.LinkRelationAttribute":[[0,1,1,"","LinkRelationAttributeDefinition"]],"volue.mesh.LinkRelationVersion":[[0,2,1,"","target_object_id"],[0,2,1,"","valid_from_time"]],"volue.mesh.Object":[[0,2,1,"","attributes"],[0,2,1,"","id"],[0,2,1,"","name"],[0,2,1,"","owner_id"],[0,2,1,"","owner_path"],[0,2,1,"","path"],[0,2,1,"","type_name"]],"volue.mesh.OwnershipRelationAttribute":[[0,1,1,"","OwnershipRelationAttributeDefinition"]],"volue.mesh.RatingCurveSegment":[[0,2,1,"","factor_a"],[0,2,1,"","factor_b"],[0,2,1,"","factor_c"],[0,2,1,"","x_range_until"]],"volue.mesh.RatingCurveVersion":[[0,2,1,"","valid_from_time"],[0,2,1,"","x_range_from"],[0,2,1,"","x_value_segments"]],"volue.mesh.Timeseries":[[0,1,1,"","Curve"],[0,1,1,"","PointFlags"],[0,1,1,"","Resolution"],[0,3,1,"","__init__"],[0,4,1,"","is_calculation_expression_result"],[0,4,1,"","number_of_points"],[0,2,1,"","schema"]],"volue.mesh.Timeseries.Curve":[[0,2,1,"","PIECEWISELINEAR"],[0,2,1,"","STAIRCASE"],[0,2,1,"","STAIRCASESTARTOFSTEP"],[0,2,1,"","UNKNOWN"]],"volue.mesh.Timeseries.PointFlags":[[0,2,1,"","MISSING"],[0,2,1,"","NOT_OK"],[0,2,1,"","OK"],[0,2,1,"","SUSPECT"]],"volue.mesh.Timeseries.Resolution":[[0,2,1,"","BREAKPOINT"],[0,2,1,"","DAY"],[0,2,1,"","HOUR"],[0,2,1,"","MIN15"],[0,2,1,"","MONTH"],[0,2,1,"","UNSPECIFIED"],[0,2,1,"","WEEK"],[0,2,1,"","YEAR"]],"volue.mesh.TimeseriesAttribute":[[0,1,1,"","TimeseriesAttributeDefinition"]],"volue.mesh.TimeseriesResource":[[0,2,1,"","curve_type"],[0,2,1,"","name"],[0,2,1,"","path"],[0,2,1,"","resolution"],[0,2,1,"","temporary"],[0,2,1,"","timeseries_key"],[0,2,1,"","unit_of_measurement"],[0,2,1,"","virtual_timeseries_expression"]],"volue.mesh.UserIdentity":[[0,2,1,"","display_name"],[0,2,1,"","identifier"],[0,2,1,"","source"]],"volue.mesh.VersionInfo":[[0,2,1,"","name"],[0,2,1,"","version"]],"volue.mesh.VersionedLinkRelationAttribute":[[0,1,1,"","VersionedLinkRelationEntry"]],"volue.mesh.VersionedLinkRelationAttribute.VersionedLinkRelationEntry":[[0,2,1,"","versions"]],"volue.mesh.XyCurve":[[0,2,1,"","xy"],[0,2,1,"","z"]],"volue.mesh.XySet":[[0,2,1,"","valid_from_time"],[0,2,1,"","xy_curves"]],"volue.mesh.aio":[[0,1,1,"","Connection"]],"volue.mesh.aio.Connection":[[0,1,1,"","Session"],[0,3,1,"","connect_to_session"],[0,3,1,"","create_session"],[0,3,1,"","get_user_identity"],[0,3,1,"","get_version"],[0,3,1,"","revoke_access_token"]],"volue.mesh.aio.Connection.Session":[[0,3,1,"","close"],[0,3,1,"","commit"],[0,3,1,"","create_object"],[0,3,1,"","delete_object"],[0,3,1,"","forecast_functions"],[0,3,1,"","get_attribute"],[0,3,1,"","get_object"],[0,3,1,"","get_rating_curve_versions"],[0,3,1,"","get_timeseries_attribute"],[0,3,1,"","get_timeseries_resource_info"],[0,3,1,"","get_xy_sets"],[0,3,1,"","history_functions"],[0,3,1,"","open"],[0,3,1,"","read_timeseries_points"],[0,3,1,"","rollback"],[0,3,1,"","search_for_attributes"],[0,3,1,"","search_for_objects"],[0,3,1,"","search_for_timeseries_attributes"],[0,3,1,"","statistical_functions"],[0,3,1,"","transform_functions"],[0,3,1,"","update_link_relation_attribute"],[0,3,1,"","update_object"],[0,3,1,"","update_rating_curve_versions"],[0,3,1,"","update_simple_attribute"],[0,3,1,"","update_timeseries_attribute"],[0,3,1,"","update_timeseries_resource_info"],[0,3,1,"","update_versioned_link_relation_attribute"],[0,3,1,"","update_xy_sets"],[0,3,1,"","write_timeseries_points"]],"volue.mesh.calc":[[0,0,0,"-","common"],[0,0,0,"-","forecast"],[0,0,0,"-","history"],[0,0,0,"-","statistical"],[0,0,0,"-","transform"]],"volue.mesh.calc.common":[[0,1,1,"","Timezone"]],"volue.mesh.calc.common.Timezone":[[0,2,1,"","LOCAL"],[0,2,1,"","STANDARD"],[0,2,1,"","UTC"]],"volue.mesh.calc.forecast":[[0,1,1,"","ForecastFunctions"],[0,1,1,"","ForecastFunctionsAsync"]],"volue.mesh.calc.forecast.ForecastFunctions":[[0,3,1,"","get_all_forecasts"],[0,3,1,"","get_forecast"]],"volue.mesh.calc.forecast.ForecastFunctionsAsync":[[0,3,1,"","get_all_forecasts"],[0,3,1,"","get_forecast"]],"volue.mesh.calc.history":[[0,1,1,"","HistoryFunctions"],[0,1,1,"","HistoryFunctionsAsync"]],"volue.mesh.calc.history.HistoryFunctions":[[0,3,1,"","get_ts_as_of_time"],[0,3,1,"","get_ts_historical_versions"]],"volue.mesh.calc.history.HistoryFunctionsAsync":[[0,3,1,"","get_ts_as_of_time"],[0,3,1,"","get_ts_historical_versions"]],"volue.mesh.calc.statistical":[[0,1,1,"","StatisticalFunctions"],[0,1,1,"","StatisticalFunctionsAsync"]],"volue.mesh.calc.statistical.StatisticalFunctions":[[0,3,1,"","sum"],[0,3,1,"","sum_single_timeseries"]],"volue.mesh.calc.statistical.StatisticalFunctionsAsync":[[0,3,1,"","sum"],[0,3,1,"","sum_single_timeseries"]],"volue.mesh.calc.transform":[[0,1,1,"","Method"],[0,1,1,"","TransformFunctions"],[0,1,1,"","TransformFunctionsAsync"]],"volue.mesh.calc.transform.Method":[[0,2,1,"","AVG"],[0,2,1,"","AVGI"],[0,2,1,"","FIRST"],[0,2,1,"","LAST"],[0,2,1,"","MAX"],[0,2,1,"","MIN"],[0,2,1,"","SUM"],[0,2,1,"","SUMI"]],"volue.mesh.calc.transform.TransformFunctions":[[0,3,1,"","transform"]],"volue.mesh.calc.transform.TransformFunctionsAsync":[[0,3,1,"","transform"]],volue:[[0,0,0,"-","mesh"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"],"4":["py","property","Python property"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:property"},terms:{"0":[0,2,5,8,10,12,17,18,19,20],"00":12,"0000":2,"000000000000":2,"0000000b":2,"0001":2,"01":[0,20],"04":1,"09":3,"0max":[0,10],"0min":[0,10],"1":[0,2,5,6,8,10,11,12,16,17,18,19,20,21,22],"10":[0,2,8,10,11,12,17,21],"100":[12,22],"1000":2,"100000f7":3,"101":[1,22],"102":22,"1073741824":0,"109":22,"11":12,"113":22,"115":22,"116":22,"12":[2,8,12,19,22],"120":22,"122":22,"123e4567":[2,16],"125":22,"12d3":[2,16],"13":12,"133":22,"134":22,"135":22,"138":22,"14":22,"1468":3,"151":22,"153":22,"156":22,"157":22,"161":22,"164":22,"172":1,"178":22,"180":17,"183":22,"19":19,"1970":[0,20],"1st":0,"2":[0,2,5,8,10,12,16,17,19],"20":1,"2016":[2,8],"2019":12,"2020":12,"2021":[12,21],"203":22,"2078":[0,1,2],"22":[12,19],"24":[0,2,8,10,12],"26":3,"27":12,"29912":3,"2nd":0,"3":[0,2,5,6,8,10,11,12,16,17,18,19,20],"31":12,"32":[0,12,20],"33554432":0,"3600":[0,10],"37":12,"3c3957c538a0":2,"3ecf8ab0e2d4":21,"3rd":0,"4":[0,2,5,8,12,19],"4299":21,"45":12,"4b0a":2,"5":[0,2,8,10,11,12,17,22],"50":12,"50051":[1,18,21],"55":[10,12],"556642440000":[2,16],"59":3,"6":[0,2,10,12,19],"64":[0,12,17],"65":12,"667000000":3,"67108864":0,"7":[0,5,6,8,10,12,18,22],"72":[2,8],"8":[0,2,5,6,10,18,22],"801896b0":21,"86400":[0,10],"87":12,"874a":21,"88":1,"8b60":2,"9":[5,6,17,18,21,22],"96":12,"99":18,"boolean":[0,11],"break":[0,10],"byte":0,"case":[0,2,3,5,8,12,14,18,22],"class":[0,10,11,17],"default":[0,1,6,11,18,20],"do":[1,2,5,6,8,19,20,21],"enum":0,"final":[0,1,21],"float":[0,12,17,20],"function":[1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,20,22],"import":[1,2,7,8,16,18,20,21],"int":[0,2,8,10,11],"long":[0,1,8,10],"new":[0,1,2,5,6,10,11,14,16,20,21],"return":[0,1,2,8,10,11,22],"true":[0,2,3,8,14,21],"try":[0,1,2,3,5,8,16,21],"while":[8,10],A:[0,2,4,8,10,11,12,14,15,16,17,20],AND:[0,14],And:1,As:[1,6,8,11,20],At:1,By:[0,1,13],For:[0,1,3,6,10,11,12,14,17,18,20],IT:1,If:[0,1,2,3,5,6,8,10,14,16,18,19],In:[0,1,3,8,11,12,17,18],Is:[0,3,10],It:[0,6,10,11,13,14,18,20],NOT:13,No:[0,2,8],OR:[0,2,14],On:1,One:[15,20],Or:[1,2,6],Such:[11,12],That:[2,20],The:[0,1,2,5,6,8,10,11,13,14,15,16,17,19,20],Then:[1,21],There:[0,6,11,13,20],These:[2,6,17,19,20,21],To:[0,1,5,6,7,12,14,15,17,19,20,21],__init__:0,__main__:[1,2,8,16,18],__name__:[1,2,8,16,18],_attribut:[0,10],_authent:[0,1],_common:0,_connect:0,_get_connection_info:[1,2,8,16,18],_object:[0,10],_timeseri:[0,10],_timeseries_resourc:0,a1:0,a2:0,a3:0,a456:[2,16],a4:0,a5:0,aa1b:2,abl:[1,6,7,8,14,15,19,20,21],about:[0,1,10,16,21,22],abov:[0,1,3,6,10,11,15,17],accept:[0,2,8,11,14,22],access:[0,2,6,9,10,14,15],account:[0,1,2],accumul:[0,10],aconnect:[1,2],acquir:0,action:0,activ:[0,1,6,11,12,13,15,17,22],actual:[0,11,17,20],ad:[0,1,2,6,11,15,22],add:[1,5,6],addit:[6,11,12,21],addition:[0,11,12],address:[1,2,3,6,8,15,16,18,21],adjust:[2,8,12],admin_serv:1,adus:0,affect:[12,16],after:[0,1,6,10,11,16],against:1,aggreg:11,aio:[1,2,5,8],aka:8,algorithm:20,all:[0,1,2,3,6,8,10,11,13,14,19,20,21],allevi:20,allow:[0,1,19],along:6,alpha:5,alreadi:0,also:[0,1,6,11,13,20],alwai:[0,2,8,11,14],am:5,ambigu:11,among:16,amount:20,an:[0,1,2,5,6,8,10,11,12,13,14,15,16,17,18,20,21],analyt:20,ancestor:11,ani:[0,2,3,8,10,11,12,13,16,20],anoth:[0,10,11,13,20],anyth:6,apach:[5,6,8,20],api:[4,5,14,16],append:[0,2,8,21],appli:[0,14],applic:[4,15],approxim:12,apt:1,ar:[0,1,2,3,5,6,8,10,11,12,13,14,16,17,18,19,20,21,22],arbitrari:6,architectur:7,area:[4,20],arg:0,argument:[0,2,8,10],arrai:[0,2,8,10,11],arrang:20,arrow:[0,2,5,6,8,20],arrow_t:[2,8,21],ask:[5,10,18],asset:[4,11],assist:1,associ:0,assum:[1,6,18],async:[0,2,5,8,10],asyncconnect:[1,2],asynchron:[0,1,5,10],asyncio:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],attach:16,attribut:[0,5,8,9,10,12,13,14,17,20,21,22],attributebas:[0,10],attributebasedefinit:0,attributedefinit:0,attributenam:14,attributes_filt:0,attributesfilt:0,audit:22,authent:[0,2,3,5,15,22],authenticatekerbero:[0,1],authentication_paramet:[1,2],author:[0,1,5,15],auto:[2,6],autom:6,automat:[6,22],avail:[0,1,6,10,19],available_at_timepoint:[0,10],avg:[0,10],avgi:[0,10],avoid:16,await:[2,5,8],awar:[1,2,8,21],axi:[10,17],b:[0,2,8,10,12],back:[2,8],base:[0,1,2,3,6,7,10,11,14,15],basic:[0,4,7],becaus:[0,2,8,12],becom:[0,1,11,12,13,17],been:[0,16],befor:[0,1,6,8,10],begin:12,behav:22,being:[0,10],believ:3,belong:[0,11],below:[0,1,6,8,10,17],better:11,between:[0,11,13,14],binari:6,bit:[0,1,12,17,20],black:[6,11,19],blue:11,blueprint:11,board:3,bool:0,boolcollectionattribut:0,booleanarrayattributedefinit:11,booleanattributedefinit:11,both:[0,1,2,10,20,22],bracket:14,breakpoint:[0,20],bring:6,broader:0,buffer:8,bug:[5,22],build:[6,11],built:15,c:[0,10,11,12],cach:1,calc:[2,5,8,10,14,21,22],calcul:[4,5,11,14,16],call:[0,1,2,5,6,8,11,13,15,17,20],came:0,can:[0,1,2,3,6,8,10,11,12,13,14,15,16,17,18,19,20],cancel:0,carbon:0,cardin:[11,13],cat:1,categori:10,caus:3,cc:3,center:1,certain:0,certif:[0,1,15],challeng:0,chang:[0,1,2,3,5,6,8,10,11,12,13,16,18],channel:0,channel_credenti:0,channelcredenti:0,charact:[0,1,2,10,11,14],check:[0,2,3,8,16,18],child:[0,11,14],children:2,click:6,client:[0,1,2,3,5,7,8,10,15],clone:6,close:[0,2,8,15,16,18],closest:14,cloud:6,coarser:[0,10],code:[2,3,6,18],collect:[0,4,11,13,14],column:17,com:[0,1,2,6,18,22],combin:[0,9,10],come:[6,10],command:[1,6,21],comment:2,commit:[0,2,6,16,22],common:[0,2,8,10,20,21],commun:[0,1,2,5,6,8,15,18,21,22],compani:[1,2],companyad:[1,2],compar:11,comparison:14,compat:5,complet:[0,1],complex:1,complic:1,compon:0,composit:14,compound_stmt:0,comput:[1,15,20],concaten:0,concept:[0,4,6,7,8,11,20],concurr:[0,2,8],conf:1,confidenti:3,config:[1,6],configur:[0,1,2,5,6,10,15,16,18],connect:[0,1,5,8,10,11,15,16,17,18,20,21,22],connect_to_sess:[0,2,16],consid:[0,10],consist:[0,7,11,13,14],consolid:4,constant:20,consult:[3,18],consum:20,contact:[3,18],contain:[0,2,10,11,12,17,20,21],content:0,context:0,contextmanag:0,contribut:6,control:[1,6,14],convent:13,convert:[0,1,2,8,10,12,21],coordin:0,copi:20,core:[0,3],core_pb2:0,core_pb2_grpc:0,coroutin:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],correct:[0,3,20],correctli:[3,6,22],could:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],cours:11,cover:0,creat:[0,1,2,6,8,11,15,16,18,20,21,22],create_object:0,create_sess:[0,2,8,16,18,21],credenti:[0,1,22],creek:11,criteria:[0,20,21],critic:22,csv:21,curli:14,current:[0,5,10,11],curv:[0,2,8,9,11,20],curve_typ:[0,2,8],custom:[3,4,11,21],d448:21,d:[1,12,20],dai:[0,2,8,10],daili:20,data:[0,2,4,7,8,11,15,16,18,19,20,21,22],databas:[2,4,8,10,19,20,21],datamodel:0,date:[0,10],datetim:[0,2,8,10,21],dateutil:[2,8],daylight:[0,10],db:4,debug:1,def:[1,2,8,16,18,21],default_realm:1,defin:[0,2,10,11,13,14,20],definit:[0,9,13,17],degre:17,delet:0,delete_access_token:0,delete_object:0,demonstr:[3,8],depart:1,depend:[2,5,8,11,20,22],deprec:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],descend:14,describ:14,descript:[0,11,17],design:[1,4,6,11,15,20,21],destroi:1,detail:[0,2,3,8],determin:1,dev:[1,2,8],develop:[4,5],diagram:11,dict:0,did:[2,16],differ:[0,1,2,6,7,8,10,11,16,18,20],dimension:17,direct:17,directli:[1,20],directori:[0,1,6,15,22],discard:[0,2,8],discharg:[0,12],disconnect:0,discuss:3,displai:[0,10,22],display_nam:0,distinguish:10,distribut:1,divid:[0,10],dn:1,doc:0,document:[2,5,6,8,14,17,22],doe:[0,2,3,10,11,13,16,22],domain:[0,1],domain_realm:1,don:[0,6],done:[2,8,13],dot:[0,11],doubl:[0,10,11,14,20],doublearrayattributedefinit:11,doubleattribut:[0,20],doubleattributedefinit:11,down:1,download:[6,21],driva:11,drop:6,dsgetdc:1,dst:0,dt:[2,8,21],due:[6,12],duplic:0,durat:0,e0903:3,e5df77a9:2,e89b:[2,16],e:[0,1,2,6,8,10,11,13,14,20,21],each:[0,10,11,12,13,14,17,20,21],earlier:[0,6,10],easi:6,easier:1,edit:[0,5],effici:[7,20],either:[0,1,2,3,8,14,15,16,18,20,22],element:0,elementattributedefinit:[0,11],elementcollectionattributedefinit:[0,11],els:20,email:6,email_address:6,empti:[0,10],enabl:[0,1,2,3,5,8,10,18],enabletl:3,encapsul:0,enclos:14,encod:0,encrypt:15,end:[0,2,8,10,12,21],end_tim:[0,2,8,10,21],endpoint:[1,14],energi:[0,5],energysystem:[0,11],enhanc:22,enough:[0,1,2],ent:10,entri:0,enumer:21,environ:[1,4,5,18],epoch:[0,20],equal:[0,10,14],equat:12,eros:12,error:[0,5,16,21,22],es:[1,21],especi:10,establish:21,estim:10,etc:[0,1,10,11],european:[0,10],evalu:[0,10],even:0,event:10,ever:0,everi:[10,11],everyth:[1,18],ex:14,exactli:0,exampl:[0,3,5,6,8,10,11,12,14,16,17,18,20,21,22],examplecompani:[0,1,2],except:[0,2,8,21],exclus:0,execut:6,exist:[0,2,10,14,16,20,21],exit:0,expect:[0,22],expir:1,explain:[15,17,21],explicit:[0,6,10],explicitli:0,expos:[0,10,21,22],express:[0,2,8,9,10,11,21],extens:11,extern:6,extra:[6,20],f:[0,1,2,8,12,14,16,18,21],factor:[0,12],factor_a:0,factor_b:0,factor_c:0,factori:0,fail:[1,5],fals:[0,14,21],fatal:3,field:[0,11,12,20],figur:[10,21],file:[1,6,18,21,22],filter:[0,11],financi:10,find:[0,1,2,8,10,14,20,21],finer:[0,10],finish:[0,16],finland:[0,10],first:[0,1,2,3,5,8,10,17,21,22],fit:21,fix:[0,2,10,22],flag:[0,2,8,11,20],flexibl:20,float64:[2,8],flow:[0,11],follow:[0,1,2,3,6,8,11,12,14,16,17,18,19,20,21,22],footnot:20,forc:22,forecast:[5,9,22],forecast_func:[0,10],forecast_funct:[0,10],forecast_start_max:[0,10],forecast_start_min:[0,10],forecastfunct:[0,10],forecastfunctionsasync:[0,10],form:[0,14],format:[0,1,2,6,8,20],formatt:6,formul:[0,10],formula:[0,12],found:[2,5,8,16,21],foundat:[0,10],four:13,frequent:[5,18],friendli:0,from:[0,1,2,8,10,11,14,15,16,18,19,20,21,22],from_arrai:[2,8],full:[1,11,22],full_attribute_info:0,full_nam:[0,2,8,10],further:[2,8,15,17],futur:[1,10],g:[0,1,2,6,8,11,13,14,20],gate:[11,20],gather:[2,8],gener:[0,1,2,3,6,20],get:[0,1,8,10,15,18,22],get_all_forecast:[0,10],get_attribut:0,get_event_loop:[1,2],get_forecast:[0,10],get_object:0,get_rating_curve_vers:0,get_timeseries_attribut:[0,22],get_timeseries_resource_info:0,get_token:0,get_ts_as_of_tim:[0,10],get_ts_historical_vers:[0,10],get_user_ident:[0,1,2],get_vers:[0,2,6,8,18],get_xy_set:[0,17],gettshistoricalvers:[0,10],gettz:8,getuserident:[1,2],git:[5,18,22],github:[5,18,22],give:[0,10],given:[0,2,6,8,10,11,12,16,20,21],global:[0,6],glossari:5,go:[1,6],gone:1,good:[1,6],grant:1,grei:10,group:[11,12,13,19,20],grpc:[0,1,2,5,6,8,15,18,21],gsserror:0,guarante:[0,11],guid:[0,1,5,6,21,22],ha:[0,1,2,8,10,11,12,15,16,17,21],had:13,handl:[0,1,15,22],handshak:3,has_:13,has_powerpl:13,have:[0,1,2,5,6,7,10,11,12,16,17,18,20],head:5,header:17,help:[1,6],helper:5,here:[0,1,5,6,11,18],histor:[0,10,20,22],histori:[5,9,22],history_funct:[0,10],historyfunct:[0,10],historyfunctionsasync:[0,10],hoc:0,horizont:10,host:[0,1,2,3,6,21],hostnam:[0,1,2],hour:[0,1,2,8,10,20],hourli:20,how:[0,1,2,5,6,8,10,11,17,20,21],howev:[0,10],html:0,http:[0,6,18,20,22],human:0,hydro:[0,11,20,21],hydropl:21,hydropow:11,i:[0,2,5,8,10,12,14],id:[0,2,4,6,11,16,21],idea:1,ideal:1,ident:0,identifi:[0,2,10,11,13,16,20],ignor:[0,10,14],imag:10,implement:[8,22],improv:20,includ:[0,1,3,10,20],inclus:0,incom:15,inconsist:22,index:[0,5,17],indic:[0,2,8,10,11,13,17,19],individu:2,info:[1,2],inform:[0,1,3,7,8,10,11,16,17,18,20,21],infrastructur:[4,11],inherit:11,ini_opt:19,init_definit:0,initi:6,innerdalsvannet:11,input:[0,14],insecur:[0,15,22],insensit:14,insert:0,insid:[0,14],instal:[1,2,4,5,19],instanc:[0,11],instanti:11,instead:[0,8,10],instruct:[3,5,6,19,21],int64arrayattributedefinit:11,int64attributedefinit:11,integ:[0,11],integr:[0,4,10],intend:[6,22],intens:20,interact:16,interfac:[1,4],intern:5,intersect:[0,14],interv:[0,2,10,20,21],introduct:5,invalid:0,investig:1,involv:0,ip:[0,1,15,21],is_calculation_expression_result:0,is_local_express:0,is_token_valid:0,issu:[1,3,5],iter:0,its:[0,10,13,18,19,20],join:[1,6],just:[11,16,22],kdc:1,kdestroi:1,kei:[0,1,2,10,20],kerbero:[0,2,5,22],kerberostokeniter:0,kind:[0,15,20],kinit:1,kit:4,know:6,known:5,krb5:1,krb5cc_1000:1,krb:1,kvotilsig:11,kwarg:0,lack:22,laid:0,languag:[0,2,4,9,10,20],larg:[8,20],larger:[0,10],largest:[0,10],last:[0,10],later:6,latest:[0,6,10],latter:[0,10],layer:15,learn:[5,8],least:0,len:[2,8,21],leq:12,less:[0,10],let:[2,8,18],level:[0,11,12,13,20],lib:0,libdefault:1,libkrb5:1,librari:[0,5,6,8,11,18,20],like:[0,3,6,11,16,17,18,20],line:[6,10,21],link:[0,9,11,22],linkrelationattribut:0,linkrelationattributedefinit:0,linkrelationvers:0,linux:5,list:[0,1,3,10,11,13,17,22],listen:15,ll:1,local:[0,1,2,8,10,11,18],local_time_zon:[2,8,21],localhost:21,localsystem:[0,1,2],locationattribut:0,log:[1,22],logic:[0,14],longer:[0,1,2,16],loos:20,lost:16,lt:[1,12],lundesokna:11,m:[6,17,18,19,21,22],machin:[1,18],maco:5,made:[0,10,18,22],mai:[0,2,6,8,11,13,14,20],main:[1,2,8,16,18,20],maintain:6,major:22,make:[1,2,6,8,14],manag:[0,6,7,11],mani:[0,6,11,13,16,20],manual:16,mark:19,mask:0,match:[11,14,21],matplotlib:21,max:[0,10],max_number_of_versions_to_get:[0,10],maximum:[0,10,11,13],maxvolum:11,mean:[0,10,14,20],measur:[0,11,12,17,20],meet:0,member:11,memori:[5,8,20],mesh:[1,2,4,12,13,16,19,21],mesh_servic:0,mesh_v2:22,meshservicestub:0,meshtek:21,messag:0,meta:[0,11,20],metadata:22,method:[0,1,2,8,10,17],might:[1,3,5,16,20],millisecond:[0,2,8,20],min15:0,min:[0,10],minim:[0,12],minimum:[11,13],minor:22,miss:[0,20],mit:5,model:[0,2,4,7,8,9,10,13,14,16,20,21,22],modifi:0,modul:[0,1,5],month:0,more:[0,1,2,5,8,10,11,17,18,20,22],most:[0,1,6,10],move:[20,21],ms:[0,2,8],much:[0,3,10,20],mulligan:21,multipl:[0,3,6,9],multipli:[0,10],must:[0,10,11],mw:17,myenergysystem:11,n:[1,14,20,21],naiv:[2,8],name:[0,1,2,6,8,10,11,13,14,17,18,22],name_mask:0,namespac:0,namespace_mask:0,nan:[0,2,8,10,12],necessari:1,necessarili:0,need:[0,1,4,5,6,8,12,14,15,19,20,21,22],neither:3,netcat:1,network:[1,3,8,15,18],networkservic:[0,1,2],new_:0,new_curve_typ:0,new_local_express:0,new_nam:0,new_owner_attribut:0,new_target_object_id:0,new_timeseries_resource_kei:0,new_unit_of_measur:0,new_vers:0,new_xy_set:0,newer:20,newli:1,next:[0,5,10,11,12,13,17],nimbu:[17,22],nltest:1,node:11,non:[0,17,18],none:[0,10,22],normal:[0,16],norwai:11,not_ok:0,note:[0,1,2,10,16],noteworthi:5,notic:[2,8],now:[0,2,8,16,18,20],number:[0,1,2,8,10,21],number_of_point:[0,2,8],numberofwindturbin:11,numer:1,numpi:20,object:[0,2,7,8,9,10,13,14,16,20,21,22],object_id:0,object_path:0,obtain:0,occur:[4,20],offici:6,often:17,ok:[0,2,8,20],old:0,omit:[0,10],one:[0,1,2,4,5,6,10,11,13,16,20],ones:0,onli:[0,1,2,8,10,11,14,20],open:[0,1,2,8,10,15,16,18],openssl_intern:3,oper:[0,1,2,8,9,10],optim:8,optimis:5,option:[0,1,2,6,8,10,11,14,21],oracl:22,order:[4,20],org:[0,6,20],organ:[2,8],other:[0,5,8,10,11,13,16,20,22],otherwis:[0,12,14],our:[1,2,5,6,8],out:[0,1,2,16,18],output:[2,8,14,18],outsid:[0,10],over:[0,4,5,8,11,12,13,15,20],overview:20,overwritten:[0,10,11],own:[0,11,13,21],owner:[0,11,13],owner_id:0,owner_path:0,ownership:[0,9,11],ownershiprelationattribut:0,ownershiprelationattributedefinit:0,p:[0,10],pa:[2,8],packag:[0,1,2,4,6,8,21],pair:[0,11,13,17],panda:[5,8,19,20,21],pandas_datafram:21,pandas_seri:[2,8],paramet:[0,1,2,10,13],parametr:14,parent:14,parenthesi:[0,10],part:[0,10,20],pass:[20,21],password:1,path:[0,2,6,8,9,10,14,20,21,22],path_and_pandas_datafram:21,pattern:21,pd:[2,8,21],pem:[0,1],per:20,perform:[0,1,4,8,10,16,20],period:[0,4,10,11,13,17,20],permiss:15,physic:[0,2,4,8,10,11,22],physicaltimeseri:20,pick:[2,8],pictur:[0,10],piecewiselinear:0,ping:[1,3],pip:[6,18,19,21,22],place:10,plant:[11,20,21],pleas:[0,1,3,8,10,18],plot:21,plot_timeseri:21,poetri:6,point:[0,1,2,4,8,10,11,12,13,14,17,20,21,22],pointflag:[0,2,8,20],port:[1,2,3,8,15,16,18,21],possibl:[1,3,6,11,16],post:21,potenti:[2,8,16],powela:[6,18,22],power:20,powerpl:11,powerplanta:11,powerplantb:11,powerplantc:11,powerproduct:11,practic:21,precis:20,predic:14,prefer:[3,5],prefix:11,prepar:[0,5],present:[0,6,8,10],preserv:20,press:3,previou:[2,8],price:0,primari:20,princip:[0,1,2],print:[1,2,8,16,18,21],problem:[3,18,20],procedur:[8,15],process:[0,2,7,8,20,21],process_respons:0,produc:14,product:[0,11,17,21],production_op:21,productionattribut:0,program:[4,20],project:[6,18,21],properli:[2,8],properti:[0,20],proto:[0,6,8,22],proto_attribut:0,proto_definit:0,protobuf:6,protocol:[1,8,15,22],provid:[0,1,2,6,8,11,15,20],pull:6,purpos:6,push:16,py:[1,6,8,18,21],pyarrow:[0,2,8],pycharm:5,pylint:19,pytest:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],python:[0,1,2,3,4,9,10,11,14,15,16,18,19,20,21],q:1,qualifi:1,queri:[0,2,8,9,22],question:[5,18],quick:18,quickest:[2,18],quickli:1,quickstart:[1,5],r:[0,1,2],rais:0,ran:[5,6],rang:[0,2,8,12,13],rate:[0,9],rather:0,ratingcurveseg:[0,21],ratingcurvevers:[0,21],rb:1,re:[1,5,6],reachabl:1,read:[0,1,3,5,8,11,19,22],read_timeseries_point:[0,2,8,21,22],read_timeseries_points_async:2,readabl:[0,11,22],real:[11,21],realm:1,reason:[1,20],receiv:[0,1,2,21],recommend:[1,5,18,22],reconnect:16,recurs:13,recursive_delet:0,red:10,refer:[0,1,2,6,8,10,11,14,17,18,20],referenc:6,referenceattributedefinit:[0,11],referencecollectionattributedefinit:[0,11],referenceseriesattributedefinit:[0,11],referenceseriescollectionattributedefinit:[0,11],reflect:12,regard:[3,18],regist:[0,1,2],regular:0,reinstal:22,reject:14,rel:[0,1,10,14],relat:[0,7,9,10,11,22],releas:6,relev:[0,10],rem:1,remot:[2,8,15,18],remov:[0,13],reorgan:22,replac:0,repli:22,report:[3,5],repositori:6,repres:[0,4,8,10,11,17,20],represent:0,request:[0,1,2,5,6,8,10,15,16,18,21],requir:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],reservoir:[11,20],reset:0,resolut:[0,2,8,9,10,11],resolv:[1,3],resourc:[0,5,16,20],respect:[14,17],respond:0,respons:[0,8,21],restrict:20,result:[0,1,2,10,11,14,16,20,21,22],retriev:[0,16,20,21],return_no_attribut:0,retyp:1,revok:[0,1,2],revoke_access_token:[0,1,2],revokeaccesstoken:0,rfc:[0,1,2],right:[6,18],river:12,rollback:[0,2,8,22],root:0,root_pem_certif:[0,1,2,8,16,18],rout:11,routin:3,row:17,rpc:[15,22],rpcerror:[0,2,8,21],rule:0,run:[0,1,3,5,6,8,10,18,22],run_until_complet:[1,2],runtim:6,runtimeerror:0,s:[0,1,3,5,6,10,11,15,17,21],same:[0,2,8,10,11,22],save:[0,6,10,21],save_timeseries_to_csv:21,save_to_csv:21,scenario:[20,21],schema:[0,2,8],scm:6,scope:[0,1,2,10,16],script:[6,18,19],sdk:[1,2,3,4,9,11,15,19,20,21],search1:14,search2:14,search:[0,4,5,8,9,10,11,16,20,21,22],search_for_attribut:0,search_for_object:0,search_for_timeseries_attribut:[0,2,8,21],search_queri:[0,10,21],second:[0,10],section:[2,5,11,21],secur:[0,1,3,15,22],sediment:12,see:[0,1,6,10,11,14,17,20,22],segment:[0,12],select:6,self:11,send:[0,1,2,8],sensibl:2,sensit:2,sensor:11,sent:[8,21],separ:[0,4,6,16,22],sequenc:[4,20],sequenti:[2,8],seri:[0,2,4,7,8,9,10,11,16,18,21,22],serial:8,serv:11,server:[0,1,2,5,6,7,8,10,16,19,20,21,22],server_kerberos_token:0,servic:[0,1,2,3,15],service_princip:0,session:[0,5,8,10,15,17,18,21,22],session_id:[0,2,16],set:[0,1,2,3,6,8,9,10,11,12,14,15,16,18,20,21,22],setup:[1,5,18,21,22],sever:[0,10,20],share:[0,5,8,16],shell:6,shift:[2,8],ship:19,should:[0,1,3,6,10,14,15,16,18],show:[1,2,8,10,11,16,18,21],show_plot:21,shown:11,signal:0,signal_final_response_receiv:0,significantli:1,similar:[0,11,13,20],simpl:[0,1,11],simplethermaltestmodel:[0,2,8],sinc:[0,20],singl:[0,10,14,22],singular:[0,11],situat:0,small:0,smallest:[0,10],sme:[6,18,22],smg:22,so:[2,6,8,11,17],softwar:[0,4,7],some:[0,1,2,3,4,5,6,8,10,11,13,14,16,18,19,20,21],some_python_packag:6,some_tzinfo:8,somepowerplant1:[0,2],somepowerplantchimney2:[2,8],someth:20,sometim:17,sort:17,sourc:[0,6,10],special:20,specif:[0,6,10,11,14,16,20,21],specifi:[0,2,10,14,19],speed:17,sphinx_copybutton:19,spn:0,squar:14,src:[3,6],ssl:3,ssl_error_ssl:5,ssl_transport_secur:3,stage:1,staircas:0,staircasestartofstep:0,standard:[0,2,6,8,10],start:[0,1,2,8,10,11,13,14,17,18,20,21,22],start_and_end_sess:[2,8],start_object_guid:[2,21],start_object_path:[2,8],start_tim:[0,2,8,10,21],state:[0,10],statement:[0,2,16],statist:[5,9],statistical_funct:[0,10],statisticalfunct:[0,10],statisticalfunctionsasync:[0,10],statu:[0,10,20],steal:16,step:[1,2,5,6,8,14,20],still:0,storag:[0,6,20],store:[0,11,12,16,17,20],storfossdammen:11,str:[0,10],stream:0,string:[0,10,11],stringarrayattributedefinit:11,stringattributedefinit:11,strongli:20,structur:[11,14,17],subject:1,subsequ:0,succe:1,succeed:1,success:[1,4,20],successfulli:[1,2],sudo:1,suffic:6,suffix:14,suggest:[3,6,20],sum:[0,2,8,10,20,22],sum_single_timeseri:[0,10],sumi:[0,10],summari:[0,10],suppli:21,support:[0,6,8,11,15,17,18,20,22],suppos:0,sure:[2,6,8],suspect:0,symbol:10,synchron:[0,1,2,10],syntax:[2,4,5,9,20],system:[1,2,6,7,8,11,16,20],t:[0,1,2,6,10,20,22],tabl:[0,2,8,10],tag:0,tag_mask:0,tailor:21,take:[0,2,8,10,14],taken:0,target:[0,2,8,10,11,13,21],target_object_id:0,task:[2,4,8,21],tcp:1,tekicc_st:21,templat:11,template_express:0,tempor:15,temporari:[0,10,16],termin:6,test:[1,4,5,6,21,22],testresourcecatalog:20,text:[12,14],than:[0,10],thei:[0,1,2,6,8,11,14,19,20],them:[0,1,2,5,6,8,11],theme:20,therefor:1,thermalcompon:[0,2,8],thermalpowertoplantref:0,thi:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],thing:[3,16],think:5,those:[11,17,20],three:[0,10,11],threshold:0,through:[1,15],ticket:1,time:[0,1,2,4,5,7,9,10,11,12,13,16,17,18,21,22],time_series_resourc:[2,8],timedelta:8,timeseri:[0,5,8,10,18,20,21,22],timeseries_attribut:[2,8,21],timeseries_attribute_id:2,timeseries_attribute_path:2,timeseries_kei:[0,2],timeseries_oper:8,timeseries_read:[2,8],timeseriesattribut:0,timeseriesattributecalcul:20,timeseriesattributedefinit:[0,11],timeseriesattributephys:20,timeseriescollectionattributedefinit:11,timeseriesresourc:[0,21],timestamp:[0,2,8,10,11,12,13,17,20,22],timezon:[0,2,8,10,21],timskei:[0,2,22],tl:[1,2,3,15,22],tmp:1,to_:13,to_area:11,to_datetim:[2,8,21],to_energymarket:13,to_hydroproduct:11,to_panda:[2,8,21],to_reservoir:11,to_watercours:11,token:[0,1,2,15],tool:[4,6,19],topic:1,toward:22,tracker:[3,5],trail:22,transform:[2,5,8,9,20,21,22],transform_funct:[0,2,8,10],transformed_timeseri:[2,8],transformfunct:[0,10],transformfunctionsasync:[0,10],transpar:1,transport:15,travers:[2,4,20],treat:[2,8],tree:11,trend:10,troubl:5,ts:[0,10],tsi:3,tsrawatt:[2,8],tupl:0,turn:3,two:[0,2,6,8,10,11,13,17],type:[0,2,8,9,10,11,13,17,21],type_nam:0,typeerror:0,tz:[2,8],tz_convert:[2,8,21],tzinfo:[2,8,21],tzlocal:[2,8],ubuntu:1,uint32:[0,2,8],undefin:20,under:1,understand:7,union:[0,10,14],uniqu:[0,10,11,20],unit:[0,11,17,20],unit_of_measur:0,univers:[0,10],unix:[0,2,8,20],unknown:0,unless:[0,6,10,20],unlik:[0,1],unprotect:10,unspecifi:0,until:[0,1,11,12,13,16,17],unvers:[0,17],up:[1,3,6,18,21],updat:[0,17,21,22],update_link_relation_attribut:0,update_object:0,update_rating_curve_vers:0,update_simple_attribut:0,update_timeseries_attribut:0,update_timeseries_resource_info:[0,22],update_versioned_link_relation_attribut:0,update_xy_set:[0,17],us:[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,19,20,22],usag:6,use_cas:21,use_case_1:21,use_case_nam:21,usecas:22,user:[0,1,2,5,8,15,16,22],user_ident:[1,2],user_princip:0,userddnsomain:1,userdnsdomain:1,userident:0,usual:[1,17],utc20220510072415:11,utc:[0,2,8,10,11,20,21],utc_tim:[0,2,8,20,21],utcdatetimearrayattributedefinit:11,utcdatetimeattributedefinit:11,uuid:[0,2,10,16,21],uuid_id:[0,2],v1alpha:0,v5:1,v:1,valid:[0,1,10,12,16],valid_from_tim:0,valu:[0,2,8,9,10,11,12,13,20],value_typ:0,valueerror:0,vannhusholdn:11,variabl:[10,18],variou:[10,22],ve:1,venv:4,verifi:[0,3,19],version:[0,4,6,8,10,11,12,13,17,18],version_info:[2,18],versionedlinkrelationattribut:[0,21],versionedlinkrelationentri:0,versioninfo:0,versions_onli:0,vertic:10,via:[10,11,20],view:[6,16],virtual:[0,4,6,10,11,18,22],virtual_timeseries_express:0,visual:[17,21,22],volu:[1,2,3,5,6,8,10,14,15,16,17,18,20,21],volum:0,vs:8,vz:1,wa:0,wai:[0,2,6,8,10,15,16,18,22],wait:[0,8],walk:14,want:[0,2,6,16,18,20,21],warn:[2,16],water:[11,12,20],watercours:12,we:[1,2,6,11,12,17,18,20,21],weather:10,week:0,well:[1,13],were:[13,21],what:[0,2,5,10,11,17,19],when:[0,1,2,3,6,10,11,14,15,16,20,22],where:[0,6,11,12,13,14,16,17],wherea:[11,20],which:[0,1,2,8,10,11,12,13,14,15,16,17,18,19,20,21],whose:14,why:2,win:0,wind:[0,17],window:[5,6],winkerbero:[0,1,2],with_kerbero:1,within:[0,2,10,14,15,16,18],without:[0,1,2,3,10,11,16],wizard:6,won:[1,22],work:[0,1,4,5,6,7,8,10,16,20,21,22],workspac:[15,16],world:[1,11],would:[0,1,2],write:[0,1,4,5,6,8,10,19,21,22],write_timeseries_point:[0,2,8],written:[2,11,19],wrong:5,wrong_version_numb:3,x:[0,12,17],x_range_from:[0,12],x_range_until:[0,12],x_value_seg:0,xy:[0,9],xy_curv:0,xy_set:0,xycurv:[0,17,21],xyset:[0,17,21],xysetattribut:[0,17],xyz:22,xyzseriesattribut:[0,17],y:[0,17],year:0,yet:[0,2,8],you:[0,1,2,3,5,6,8,10,11,14,15,16,17,18,19,20,21,22],your:[1,2,3,5,6,18,21],your_python_script:6,yourself:1,z:[0,17],zero:0,zone:[0,2,10,21]},titles:["API documentation","Authentication","Examples","Frequently Asked Questions","Glossary","Welcome to Mesh Python SDK","Installation","An introduction to Mesh","Mesh Python SDK","Mesh concepts","Mesh functions","Mesh object modelling","Rating curves","Relations","Mesh search language","Mesh server","Session","XY-sets in Mesh","Quickstart guide","Tests","Time series","Use cases","Versions"],titleterms:{"0":22,"2":22,"3":22,"4":22,"case":21,"do":3,"function":[0,10,21],"new":22,The:21,access:17,add:21,aio:0,alpha:22,am:3,an:7,api:0,ask:3,asynchron:2,attribut:[2,11],authent:1,author:2,bug:3,calc:0,calcul:[0,10,20],call:18,chang:22,combin:14,compat:22,concept:9,configur:[3,21],connect:[2,3],criteria:14,curv:[12,17],date:8,definit:[10,11],depend:[6,21],develop:6,document:0,edit:21,environ:6,error:3,exampl:[1,2],express:20,fail:3,featur:[3,5,22],first:18,forecast:[0,10],found:3,frequent:3,get:[2,3,5,21],git:6,github:6,glossari:4,grpc:3,guid:18,have:3,help:[3,5],helper:21,histori:[0,10],i:3,indic:5,instal:[6,18,21,22],instruct:22,intern:1,introduct:7,issu:22,kerbero:1,known:22,languag:14,link:13,linux:1,maco:1,mesh:[0,3,5,6,7,8,9,10,11,14,15,17,18,20,22],mit:1,model:11,more:3,multipl:14,need:3,next:18,object:11,one:3,oper:14,other:3,ownership:13,panda:2,path:11,physic:20,prefer:21,prepar:19,prerequisit:[5,18],pycharm:6,python:[5,6,8,17,22],queri:14,question:3,quickstart:[2,18],ran:3,rate:12,read:2,recommend:6,refer:5,relat:13,request:3,resolut:20,run:[2,19,21],sdk:[5,6,8,17,22],search:[2,14],seri:20,server:[3,15,18],session:[2,16],set:17,setup:6,ssl_error_ssl:3,start:5,statist:[0,10],step:18,syntax:14,tabl:5,test:[3,19],them:3,think:3,time:[8,20],timeseri:2,transform:[0,10],travers:14,type:20,us:[2,17,21],user:6,valu:17,version:[2,5,22],virtual:20,volu:0,welcom:5,what:3,window:1,work:2,write:2,wrong:3,xy:17,zone:8}})