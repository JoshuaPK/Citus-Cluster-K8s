# HOWTO set up a complete Citus K8s Cluster in 87 Easy Steps #

## Procure Infrastructure ##

1. Obtain Basic Infastructure
   1. Obtain 3 CentOS 7 machines, either physical or VM.
   2. First machine should be named `kubemaster` and set to static IP of 192.168.122.2
   3. Second and third machines should be named `kube2` and `kube3` and be set to static IP of 192.168.122.3 and .122.4
   4. Update all machines to latest CentOS via `yum update`.
   5. Install packages noted in **Appendix A** on _kubemaster_.
   6. Install packages noted in **Appendix B** on _kube2_ and _kube3_.
   7. Create the `/etc/hosts` file shown in **Appendix C** on all three machines.
   8. Create a user _kubeuser_ on _kubemaster_.

2. Create CA Certificate
   1. Using EasyRSA or some other utility, create a CA certificate for the domain `kubedom`.  This can be done on _kubemaster_ to make things easy.
   2. Generate a server certificate for _kubemaster_.

3. Set up Docker Repository
   1. On _kubemaster_, create a directory for registry artifacts; perhaps it is called `/home/kubeuser/registry`.
   2. Make _registry_ the current directory.
   3. Create a directory, `certs` under _registry_.
   4. Copy the .key and .crt files for _kubemaster_ (the files you generated under _Create CA Certificate_ above) into _certs_.
   5. Copy the CA certificate you created under the _Create CA Certificate_ section above into _certs_.
   6. Create a passwd file for authentication: enter the command `htpasswd -B -c regpasswd kubeuser`. Then, when prompted for the password, enter `kubeuser`.
   7. Enter the `run_repository.sh` file shown in **Appendix C**.
   8: Enter the command: `docker login kubemaster:444`; enter _kubeuser_ when prompted for username and the same when prompted for password. 

4. Set up the Secrets in the Docker server for use with Kubernetes
   1. See https://kubernetes.io/docs/concepts/containers/images/#using-a-private-registry for more information.

## Procure Code ##

5. Download a docker file to use for testing
   1. Download a docker file for some application.  (This is the Dockerfile itself used to build the machine image- it is not the actual machine image.)
   2. Modify the Dockerfile to include something unique for your situation.
   3. Run `docker build -t someapp:v1 .` in the directory containing the Dockerfile.
   4. Run `docker tag someapp:v1 kubemaster:443/kubeuser/someapp-image:latest`
   5. Run `docker push kubemaster:443/kubeuser/someapp-image:latest` 
