# NMS Project on Kubernetes
## Summary
Tree level directory structure:
```
├── charts : A directory containing any charts upon which this chart depends, can contain multi sub-chart
├── Chart.yaml : A YAML file containing information about the chart and also define the dependencies or condition for sub-chart
├── README.md : Just README file that I note the guide for you
└── values.yaml : The default configuration values for this chart, can call as a global values file, on this file you can override the values of any sub-chart
```

---
## How to Setup
### `You can setup with 2 options`
1. `The easy way:` just run ansible-playbook to setup all flow and startup NMS application
2. `The hard way:` run ansible-playbook to create k8s cluster first, then edit the values.yaml file and start NMS application yourself

---
## `1. The easy way`
### Step 1: Prepare
- Prepare 3 clean VM node for this setup
- Clone the Installation repo https://github.com/moophat/SVTECH-installation-automation
    ```
    cd /opt
    git clone https://github.com/moophat/SVTECH-installation-automation
    ```
- Preview the nms_k8s.yml playbook and edit inventory file at /opt/SVTECH-installation-automation/inventories/default/nms_k8s_inventory.yml
    - `nms_k8s_inventory.yml` example:
    ```
    all:
    children:
        k8s:
        hosts:
            node-1:
            ansible_host: 10.98.0.140
            IP: 10.98.0.140
            master: true
            init_node: True
            schedule: true
            priority: 120
            if_name: ens192
            node-2:
            ansible_host: 10.98.0.141
            IP: 10.98.0.141
            master: true
            schedule: true
            priority: 110
            if_name: ens192
            node-3:
            ansible_host: 10.98.0.142
            IP: 10.98.0.142
            master: true
            schedule: true
            priority: 100
            if_name: ens192
    vars:
        # Common variables
        ## If number of node = 1 ==> Ignore VIP and virtual_router_id or set it ""
        VIP: "10.98.0.143"
        virtual_router_id: 143
        timezone: "Asia/Ho_Chi_Minh"
        prefix: staging

        # Variables for Kubernetes
        cni: weave    # weave or calico
        kubernetes_system_id: test
        kubernetes_force_reset: true
        kubernetes_version: 1.22.7
        kubernetes_cluster_name: kubernetes
        pod_subnet: 192.168.1.0/24
        service_subnet: 192.168.2.0/24

        # Variables for HAPROXy
        haproxy_mgt_port: 8080
        haproxy_mgt_user: juniper
        haproxy_mgt_password: juniper@123
        mail_from: ha.do@svtech.com.vn
        mail_to: ha.do@svtech.com.vn

        # Variables for passwordless SSH
        ansible_port: 22
        ansible_ssh_user: root
        ansible_ssh_pass: juniper@123

        # Variables for create new SSH admin user
        admin_user: juniper
        admin_password: juniper@123

        # Variables for NMS application
        ## if number of node = 1 ==> longhorn_persistence_replica will auto = 1
        longhorn_persistence_replica: 3
        ## If number of node = 1 ==> Ignore Loadbalancer_pool and Loadbalancer_IP or set it ""
        Loadbalancer_pool: "10.98.0.144/32"
        Loadbalancer_IP: "10.98.0.144"

        GH_USERNAME: moophat

        # Input tag/branch folowing below intructons:
        # For Tag:
        ## <tag_name>: the tag that exist on the repo (example v1.1.0)
        ## latest: the latest tag that exist on the repo
        ## null or "None" or "": Not specific the tag name and clone the newest commit

        ## The branch "master" or "main" is default. If you want to change the branch name. You can change tag: <branch name>
        list_github_repo:
        - name: SVTECH-Junos-Automation
            tag: ""
        - name: SVTECH_Projects_Container
            tag: ""

        # CI/CD variables
        use_private_registry: "false"
        private_registry: 10.98.0.121:5000

        CI: "false"
        # Input the image name for testing. Multi test images can be input as "image1,image2,image3"
        images_test: ""
        # Input the test tag name for the above images to testing
        tag_test: test
    ```
Flowing to the defined node vars in inventory, you can set the number of master node and worker node base on the master var
And you can also make the master node work as worker by set schedule=True

The default I've defined : 3 node master and also are worker.
There are 1 active master at time (which has VIP is active)

- Change the `IP` of the node and some specific info like:
    - `VIP`: VIP for k8s cluster (HA and falover)
    - `virtual_router_id`: for keepalived
    - `pod_subnet`: for k8s cluster
    - `service_subnet`: for k8s cluster
    - `cni`: change it if you want (weave or calico)
    - `longhorn_persistence_replica`: change it if you want
    - `Loadbalancer_pool`: Loadbalancer pool for NMS application
    - `Loadbalancer_IP`: Loadbalancer IP for NMS application
    - `list_github_repo`: you can change the tag for specific version of repo (for testing)
    - `use_private_registry`: set true if you want to use docker private registry
    - `CI`: set true for CI testing

### Step 2: Run NMS installation
- Start setup NMS

    ```
    cd /opt/SVTECH-installation-automation
    ansible-playbook nms_k8s.yml -i inventories/default/nms_k8s_inventory.yml
    ```

- After installation done check that all pod and service is running
    ```
    kubectl get pods
    kubectl get svc
    ```

- In /opt/SVTECH_Projects_Container/kubernetes/nms_project you can see the file `install_command.sh`, this file save the helm install command that override some value in file values.yaml to start the NMS application
    ```
    helm install nms /opt/SVTECH_Projects_Container/kubernetes/nms_project \
    --set global.timezone=Asia/Ho_Chi_Minh \
    --set metallb.configInline.address-pools[0].name=default \
    --set metallb.configInline.address-pools[0].protocol=layer2 \
    --set metallb.configInline.address-pools[0].addresses[0]=10.98.0.144/32 \
    --set proxy.service.loadBalancerIP=10.98.0.144 \
    --set rundeck.rundeckConfig.HOST_IP=10.98.0.144 \
    --set debuger.service.externalIPs[0]=10.98.0.143 \
    --set mariadb-galera.service.externalIPs[0]=10.98.0.144 \
    --set influxdb.influxdb.service.externalIPs[0]=10.98.0.144 \
    --set icinga2.master.service.externalIPs[0]=10.98.0.144 \
    --set icinga2-report.service.externalIPs[0]=10.98.0.144 \
    --set rundeck-option-provider.service.externalIPs[0]=10.98.0.144 \
    --set neo4j.neo4j.service.externalIPs[0]=10.98.0.144 \
    --set proxy.replicaCount=2 \
    --set mariadb-galera.replicaCount=3 \
    --set influxdb.influxdb.replicaCount=3 \
    --set icinga2.master.replicaCount=2 \
    --set icinga2.satellite.replicaCount=3 \
    --set postfix.replicaCount=2 \
    --set thruk.replicaCount=2 \
    --set nagvis.replicaCount=2 \
    --set gitlist.replicaCount=2 \
    --set grafana.replicaCount=2 \
    --set icinga2-report.replicaCount=2 \
    --set rundeck-option-provider.replicaCount=2 \
    --set neo4j.neo4j.replicaCount=0
    ```
    - If you want to get the override values changes run the bellow command to view:
        ```
        helm get values nms -o yaml
        ```
    - Or if you want to get full file values.yaml that is applied and overrided, run bellow command:
        ```
        helm get values nms -a -o yaml
        ```
- Now you can go to web with Loadbalancer_IP

    Example:
    ```
    http://10.98.0.144
    ```

## `2. The hard way`

### Step 1: K8s Cluster Environment Setup
- Prepare 3 clean VM node for this setup
- Clone the Installation repo https://github.com/moophat/SVTECH-installation-automation
    ```
    cd /opt
    git clone https://github.com/moophat/SVTECH-installation-automation
    ```

- Preview the k8s.yml playbook and edit inventory file at /opt/SVTECH-installation-automation/inventories/production/k8s_inventory.yml
    - `k8s_inventory.yml` example:
    ```
    all:
    children:
        k8s:
        hosts:
            node-1:
            ansible_host: 10.98.0.140
            IP: 10.98.0.140
            master: true
            init_node: True
            schedule: true
            priority: 120
            if_name: ens192
            node-2:
            ansible_host: 10.98.0.141
            IP: 10.98.0.141
            master: true
            schedule: true
            priority: 110
            if_name: ens192
            node-3:
            ansible_host: 10.98.0.142
            IP: 10.98.0.142
            master: true
            schedule: true
            priority: 100
            if_name: ens192
    ```
    Flowing to the defined node vars in inventory, you can set the number of master node and worker node base on the master var
    And you can also make the master node work as worker by set schedule=True

    The default I've defined : 3 node master and also are worker.
    There are 1 active master at time (which has VIP is active)

    - Change the `IP` of the node and some specific info like `VIP, virtual_router_id, pod_subnet, service_subnet`

- Start setup K8s cluster
    ```
    cd /opt/SVTECH-installation-automation
    ansible-playbook  k8s.yml -i inventories/production/k8s_inventory.yml
    ```
- Wait for the Setup done and verify K8s cluster status:
    - Make sure all node is ready
    ```
    [root@master ~]# kubectl get nodes
    NAME     STATUS   ROLES                  AGE   VERSION
    master   Ready    control-plane,master   92d   v1.20.1
    node1    Ready    control-plane,master   92d   v1.20.1
    node2    Ready    control-plane,master   92d   v1.20.1
    ```
    - And all k8s components is running

    ```
    [root@master ~]# kubectl get pods -n kube-system
    NAME                             READY   STATUS    RESTARTS   AGE
    coredns-7c78fc7cfd-hq95s         1/1     Running   0          5d17h
    coredns-7c78fc7cfd-pgkkx         1/1     Running   0          5d17h
    kube-apiserver-master            1/1     Running   10         37d
    kube-apiserver-node1             1/1     Running   12         92d
    kube-apiserver-node2             1/1     Running   9          92d
    kube-controller-manager-master   1/1     Running   92         92d
    kube-controller-manager-node1    1/1     Running   90         92d
    kube-controller-manager-node2    1/1     Running   95         92d
    kube-proxy-96jhv                 1/1     Running   4          92d
    kube-proxy-j4vgh                 1/1     Running   5          92d
    kube-proxy-wzg7d                 1/1     Running   5          92d
    kube-scheduler-master            1/1     Running   86         92d
    kube-scheduler-node1             1/1     Running   92         92d
    kube-scheduler-node2             1/1     Running   83         92d
    weave-net-gpbj4                  2/2     Running   10         92d
    weave-net-l9vt6                  2/2     Running   10         92d
    weave-net-pgczb                  2/2     Running   11         92d
    ```

### 2. Install Helm Chart tool
This is a Automation tool to deploy k8s project
Install:
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```
Verify:
```
helm version
```

---

## Getting Started

### Tree level
```
kubernetes
└── nms_project
    ├── charts
    │   ├── common
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── csv-view
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── debuger
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── gitlist
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── grafana
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── files
    │   │   │   └── ...
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── icinga2
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── icinga2-report
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── files
    │   │   │   └── ...
    │   │   ├── templates
    │   │   │   └── ...
    │   │   └── values.yaml
    │   ├── influxdb
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── files
    │   │   │   └── ...
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   └── ...
    │   │   └── values.yaml
    │   ├── mariadb-galera
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── ci
    │   │   │   └── values-production-with-rbac.yaml
    │   │   ├── files
    │   │   │   └── ...
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   └── ...
    │   │   ├── values.schema.json
    │   │   └── values.yaml
    │   ├── metallb
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── nagvis
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── neo4j
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── postfix
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── preparation
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── proxy
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── rundeck
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── rundeck-option-provider
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   ├── sharedVolume
    │   │   ├── charts
    │   │   ├── Chart.yaml
    │   │   ├── README.md
    │   │   ├── templates
    │   │   │   ├── ...
    │   │   └── values.yaml
    │   └── thruk
    │       ├── charts
    │       ├── Chart.yaml
    │       ├── files
    │       │   └── ...
    │       ├── templates
    │       │   ├── ...
    │       └── values.yaml
    ├── Chart.yaml
    ├── README.md
    ├── templates
    ├── values_template.yaml
    └── values.yaml
```

The `nms_project` is big chart that contain multi sub-chart. These sub-charts can be run alone or run with other project depend on you.
Each sub-chart has it's own values.yml file for run alone, you can define your variable to pass to the template file (on template folder).
`nms_project` has a `values.yaml` file, if you define variables here, it's will override var on sub-chart (https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)

For more information, You can read helm chart document here: https://helm.sh/docs/chart_template_guide/


### How to Start NMS Project

- Clone this repo to /opt:
    ```
    cd /opt
    git clone https://github.com/moophat/SVTECH_Projects_Container.git
    ```

- Install dependencies for longhorn:
    ```
    yum -y install iscsi-initiator-utils
    systemctl enable iscsid
    systemctl start iscsid

    yum install -y jq
    yum install -y nfs-utils
    ```

- Start Longhorn chart:
    ```
    cd /opt/SVTECH_Projects_Container/kubernetes
    helm install longhorn -n longhorn-system ./longhorn --create-namespace
    ```

- Edit values.yaml at /opt/SVTECH_Projects_Container/kubernetes/nms_project
    - Change all the `externalIPs, loadBalancerIP, metallb.configInline.address-pools[0].addresses` to your VIP and some importance var like `replicaCount` ,... to fit your case
    - You can also change the `imageRegistry` and `timezone` in the global field to override for all instead of changing each sub-chart field

- Start Project:
    ```
    cd /opt/SVTECH_Projects_Container/kubernetes/nms_project
    helm install nms .
    ```

Verify:
- Check Pods
    ```
    kubectl get pods
    ```
- Check service
    ```
    kubectl get svc
    ```
- Check configmaps
    ```
    kubectl get cm
    ```
- Check Persistent volume and Persistent volume claim
    ```
    kubectl get pv
    ```
    ```
    kubectl get pvc
    ```