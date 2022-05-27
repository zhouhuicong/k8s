kubectl -n default create role endpoint-reader --verb=get --resource=endpoints
 
kubectl -n default create serviceaccount rabbitmq
 
kubectl -n default create rolebinding endpoint-reader --role=endpoint-reader --serviceaccount=default:rabbitmq