# microservices-server
Microservice Server

# Pre-requisites
After fulfilling the pre-requisites, you can forward to each folder to setup each component

## Close the firewall (at least temporarily)
`sudo systemctl disable --now firewalld`

## Install Docker using convenient script
1. `curl -fsSL https://get.docker.com -o get-docker.sh`
2. `sudo sh get-docker.sh`

## Setup Kubernetes Cluster

### Install Kubernetes (on both master and worker nodes)
1. `sudo apt install lsb-core -y`
2. `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -`
3. `sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"`
4. `curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -`
5. Run the following
    ``` 
    cat << EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
    deb https://apt.kubernetes.io/ kubernetes-xenial main
    EOF
    ```
6. `sudo apt update`
7. `sudo apt-get install -y kubernetes-cni kubelet kubeadm kubectl`
8. `sudo apt-mark hold kubelet kubeadm kubectl`
9. `sudo systemctl daemon-reload`
10. `sudo systemctl restart kubelet` 

### Setup master node
1. `sudo swapoff -a`
2. `sudo kubeadm init --pod-network-cidr=10.244.0.0/16`
3. Note the output of above command. The above cmd will generate a join token which should be run on worker nodes after initial setup using step1. The token will expire in 24hrs. If you have forgotten to save the above received kubeadm join command, then you can create a new token and use it for joining worker nodes to the cluster using the command `sudo kubeadm token create --print-join-command`  
4. Configure kubectl, so kubectl commands can be run without root privilege
    1. `mkdir -p $HOME/.kube`
    2. `sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config`
    3. `sudo chown $(id -u):$(id -g) $HOME/.kube/config`
5. Install Kubernetes' network routing extension by `kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml`. The link may vary overtime. If so, [search `kube-flannel` on Google](https://www.google.com/search?q=kube+flannel) to find the latest link

### Setup worker node
1. `sudo swapoff -a`
2. join the master node's cluster by copy and run master's output token `sudo kubeadm join <IP:PORT --token <token> --discovery-token-ca-cert-hash sha256:<checksum>` 



