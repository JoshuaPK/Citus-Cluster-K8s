
# Introduction #

# First Steps #

1. Set up Kube cluster:
   https://www.howtoforge.com/tutorial/centos-kubernetes-docker-cluster/
2. Create Citus docker container
2. Create and Deploy a Docker Contanier to Kube:
   https://www.linode.com/docs/applications/containers/deploy-container-image-to-kubernetes/

# Errors Encountered #

Citus workers were stuck on Container Creating:
  https://serverfault.com/questions/728727/kubernetes-stuck-on-containercreating
  (Note that we did do the --pod-network-cidr= on kubeadm init)
Because:
  https://stackoverflow.com/questions/44305615/pods-are-not-starting-networkplugin-cni-failed-to-set-up-pod/51091698
    (That did not solve anything)
  I did this and found that the worker nodes had status of CrashLoopBackOff:
    https://linuxacademy.com/community/posts/show/topic/32443-flannel-error-while-creating-deployment
  https://stackoverflow.com/questions/52098214/kube-flannel-in-crashloopbackoff-status
    I remember that I loaded Flannel AFTER joining the nodes.  So I wiill reset then re-join them.  Did not work
  https://stackoverflow.com/questions/50833616/kube-flannel-cant-get-cidr-although-podcidr-available-on-node
    Run the 'get nodes' command in that post, and I get "connection to localhost:8080 was refused"
  Reviewing the kubeadm init command as well as the above Stack Overflow article I see that the option
    '--pod-network-cidr' has nothing to do with the actual network assigned to the hosts.  So it
    really should be 10.244.0.0/16, even on my system.
    THIS WAS THE PROBLEM.

Next Problem:
container "citus-worker" in pod "citus-worker-deployment-b668b5bf6-5jdj6" is waiting to start: trying and failing to pull image
I had to modify the docker server to listen on a tcp port (/etc/sysconfig/docker) and put the address of the
listening port in the Deployment config files.  To solve this I will need to configure a secret in the Docker server
as well as Kubes:
https://kubernetes.io/docs/concepts/containers/images/#using-a-private-registry

## Creating a Private Registry ##

https://github.com/duffqiu/docker-registry-systemd
https://docs.docker.com/registry/deploying/
...of course a username and password are REQUIRED for Kubes to use the local registry... which requires TLS...

When creating htpasswd file remember to use -B option for bcrypt format
https://github.com/docker/distribution/issues/2565


## Update 02 Aug ##

We are to the point where the private registry works properly, all we need to do is properly configure K8s to pick up the images
from that private registry...

## Update 10 Aug ##

Everything pulls from the registry properly now.  Next step is to get the worker nodes to communicate with the master and membership,
and also add a role to the master such that we can query stuff.

### Orchestration ###

The citus_membership container is described here: https://github.com/citusdata/workerlist-gen
workerlist-gen wraps a single docker-gen process, which responds to Docker events by regenerating a worker list file. This file will contain the hostnames of all containers with a com.citusdata.role label value of Worker. All workers are assumed to be running a Citus instance on port 5432.

The worker list file will be written to /etc/citus/pg_worker_list.conf any time the set of worker nodes changes. After updating the file, docker-gen will call master_initialize_node_metadata (using psql) against a container named citus_master, forcing the Citus instance to repopulate its worker list table. psql expects to connect over a socket.

https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/

see the helper container

So the K8s projects I found indicate that when a new worker is created, it adds the machine name of the worker to a file named (what?) that is shared among all of the containers.  Is this file read by the master server itself?  Or does that Python script on the "membership" server have something to do with it?

Creating the shared Volume to share the workers textfile:  https://github.com/kubernetes/kubernetes/issues/45000
https://carlos.mendible.com/2019/02/10/kubernetes-mount-file-pod-with-configmap/  (This did not lead anywhere)

We will just mount a whole config directory, and copy the file via the lua script.  This may require distribution of ssh keys... and remember there is no sshd on the postgres master.

ALL WORKER NODES REQUIRE nfs-utils package!

TODO: Lua script: does the lua-filesystem package implement flock or lockf?  Test it on a file on a NFS share!
Do not- the citus worker images already have Python.  Use that.
Python does not work.  Have to use Lua 5.2 due to lua-posix does not include for 5.3.
So the lua-posix in Debian Buster (upon which the official PG Docker image is based) is missing important functionalty.
Need to download Debian Buster, then compile our own lua-posix for 5.3.

NFS Notes: Need to use v4 so locks work correctly.
https://docs.okd.io/latest/install_config/persistent_storage/persistent_storage_nfs.html
Note NFS 4.1 option on this volume: https://kubernetes.io/docs/concepts/storage/persistent-volumes/

FORGET NFS.  Going with MQTT-based solution instead.

92.168.122.3   kube2                                                                                                                                                                                                               
192.168.122.4   kube3                                                                                                                                                                                                               
192.168.122.2   kubemaster                                                                                                                                                                                                          
192.168.122.10  citus-k8s-mm 

Actually it is both:
1. Master node boots up, and writes its hostname to MASTER_HOSTNAME
2. Member Manager boots up, and writes its hostname to MEMBER_MANAGER_HOSTNAME
3. Workers consult those files to know where to connect to.


Now DNS is an issue- each container cannot resolve names of other containers...
https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/

I wonder if I can just get a shell on the coredns containers and poke around there??

hostname -a somedomain.as to list all records.  Keep in mind that even with a StatefulSet, the hostnames contained
in DNS include a lot of subdomains.  Get the full hostname with 'hostname -f'

NOTES ON PERSISTENT VOLUMES:
kubectl get pv | tail -n+2 | awk '{print $1}' | xargs -I{} kubectl patch pv {} -p '{"metadata":{"finalizers": null}}'  (For when they won't delete)

Why is the member manager rebooting itself every 15 minutes?

Something is wrong with the MQTT callbacks- they aren't called when messages appear.

Now MQTT callback works, it generates the file properly, the file is in the right location on master, yet
calls to master_initialize_node_metadata fail.
Per this, they deprecated that config setting- it's all direct queries to the master database now.
https://github.com/citusdata/docker/issues/18

# Questions #

1. How to set up the Citus cluster so that it communicates properly with other Citus nodes within the whole
   Kubernetes environment.

# Update Sept 22 2019#

Now that everything works, we need to change the volumes so that they don't use NFS- make this easy to deploy via helm chart where there may not be a NFS server.

## Adventures with Helm ##

https://stackoverflow.com/questions/53086454/helm-error-no-available-release-name-found-same-error-different-problem
https://scriptcrunch.com/helm-error-no-available-release/

