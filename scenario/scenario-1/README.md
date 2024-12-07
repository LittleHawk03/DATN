
# kubectl --token=TOKEN auth can-i --list
Resources           Non-Resource URLs   Resource Names   Verbs
*.*                 []                  []               [*]
                    [*]                 []               [*]

# kubectl auth can-i --list
Resources           Non-Resource URLs    Resource Names   Verbs
selfsubj...k8s.io   []                   []               [create]
selfsubj...k8s.io   []                   []               [create]
pods                []                   []               [get create list]

# kubectl --token=TOKEN  get secrets -A  
NAMESPACE      NAME                                     TYPE                 DATA   AGE
kube-system    k8s-serving                              kubernetes.io/tls    2      19d
kube-system    sh.helm.release.v1.traefik-crd.v1        helm.sh/release.v1   1      19d
kube-system    sh.helm.release.v1.traefik.v1            helm.sh/release.v1   1      19d
kube-system    interdata...node-password.k3s            Opaque               1      19d
kube-system    interdata...node-password.k3s            Opaque               1      19d
kma-postgres   postgres-postgresql                      Opaque               2      14d
kma-postgres   sh.helm.release.v1.postgres.v1           helm.sh/release.v1   1      14d

$ kubectl get pods -n scenario-1        
NAME                READY   STATUS    RESTARTS   AGE
compromised-pod-2   1/1     Running   0          52m
alpine              1/1     Running   0          52m
nginx               1/1     Running   0          52m
escape              1/1     Running   0          37m