# ecofin-backend

helm upgrade -i rancher rancher-latest/rancher --create-namespace --namespace cattle-system --set hostname=108.181.199.97 --set bootstrapPassword=bootStrapAllTheThings --set replicas=1 --set ingress.enabled=false

helm upgrade -i rancher rancher-latest/rancher \
  --create-namespace \
  --namespace cattle-system \
  --set hostname=108.181.199.97 \
  --set bootstrapPassword=bootStrapAllTheThings \
  --set replicas=1 \
  --set ingress.tls.source=none


NS=`kubectl get ns |grep Terminating | awk 'NR==1 {print $1}'` && kubectl get namespace "$NS" -o json   | tr -d "\n" | sed "s/\"finalizers\": \[[^]]\+\]/\"finalizers\": []/"   | kubectl replace --raw /api/v1/namespaces/$NS/finalize -f -

wget -q -O - https://raw.githubusercontent.com/keycloak/keycloak-quickstarts/latest/kubernetes/keycloak-ingress.yaml | \
sed "s/KEYCLOAK_HOST/keycloak.$(108.181.199.97).nip.io/" | \
kubectl create -f - -n keycloack