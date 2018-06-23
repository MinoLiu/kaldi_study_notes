# nvidia-driver

**Add "contrib" and "non-free" components to /etc/apt/sources.list, for example:**
```bash
deb http://debian.csie.ntu.edu.tw/debian/ stretch main contrib non-free
```

**Update the list of available packages. 
Install the appropriate linux-headers and kernel module packages:**
```bash
sudo apt update
sudo apt install linux-headers-$(uname -r|sed 's/[^-]*-[^-]*-//') nvidia-driver
sudo apt install firmware-linux build-essential gcc-multilib
```

This will install the nvidia-driver package. DKMS will build the nvidia module for your system, via the nvidia-kernel-dkms package. 

**Restart your system to enable the nouveau blacklist.**

# CUDA

## downgrade to gcc 4.9
- Downgrade gcc to 4.9. After CUDA is installed you can set it back to gcc 6
- To install just the drivers, the gcc 6 works. CUDA works only with gcc 4.9

### Install this packages
- TODO: Check the installation order again

```bash
package=cpp-4.9_4.9.2-10_amd64.deb 
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

package=g++-4.9_4.9.2-10_amd64.deb 
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

package=gcc-4.9_4.9.2-10_amd64.deb  
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

package=gcc-4.9-base_4.9.2-10_amd64.deb
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

package=libasan1_4.9.2-10_amd64.deb 
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

wget http://debian.csie.ntu.edu.tw/debian/pool/main/c/cloog/libcloog-isl-dev_0.18.2-1+b2_amd64.deb
sudo dpkg -i libcloog-isl-dev_0.18.2-1+b2_amd64.deb

package=libgcc-4.9-dev_4.9.2-10_amd64.deb   
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

wget http://debian.csie.ntu.edu.tw/debian/pool/main/i/isl/libisl10_0.12.2-2_amd64.deb
sudo dpkg -i libisl10_0.12.2-2_amd64.deb

package=libstdc++-4.9-dev_4.9.2-10_amd64.deb
wget http://debian.csie.ntu.edu.tw/debian/pool/main/g/gcc-4.9/$package
sudo dpkg -i $package

wget http://debian.csie.ntu.edu.tw/debian/pool/main/c/cloog/libcloog-isl4_0.18.2-1+b2_amd64.deb
sudo dpkg -i  libcloog-isl4_0.18.2-1+b2_amd64.deb
```
- Set gcc 4.9 as the default compiler

```bash
sudo unlink /usr/bin/gcc
sudo ln -s /usr/bin/gcc-4.9 /usr/bin/gcc
gcc --version
sudo unlink /usr/bin/g++
sudo ln -s /usr/bin/g++-4.9 /usr/bin/g++
```

## CUDA

- Perl stuff from the video

```bash
wget https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda_8.0.61_375.26_linux-run
sudo apt-get install libcupti-dev
./cuda_8.0.61_375.26_linux-run --tar mxvf
# Note: perl location may not be the same, 
# if install fail, go to /tmp/cuda_install_*.log check the log
sudo cp InstallUtils.pm /usr/lib/x86_64-linux-gnu/perl5/5.24/
export $PERLLIB
```

- Then install CUDA

```bash
sudo apt-get install libcupti-dev
sudo sh cuda_8.0.61_375.26_linux-run
```
Note: no need the --override thing if using gcc 4.9

### Cudnn
- Download cudnn 5.1 from the nvidia site
```bash
tar xvzf cudnn-8.0-linux-x64-v5.1-ga.tgz
sudo cp cuda/include/cudnn.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn.h /usr/local/cuda/lib64/libcudnn*
```

### Test
Install TensorFlow and Keras

```bash
sudo pip3 install keras
sudo pip3 install --upgrade tensorflow-gpu
```
- To make it usable from the notebook and for everyuser.Put this in /etc/profile:
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/lib:/usr/lib/x86_64-linux-gnu
export CUDA_HOME=/usr/local/cuda
export PATH=$PATH:/usr/local/cuda/bin
```
And append to /etc/ld.so.conf:
```bash
/usr/local/cuda/lib64
/usr/local/lib
/usr/lib/x86_64-linux-gnu
```

Test the examples (compile them first)

```bash
~/NVIDIA_CUDA-8.0_Samples/bin/x86_64/linux/release/matrixMul
```
## Set gcc 6 as default again
```bash
sudo unlink /usr/bin/gcc
sudo ln -s /usr/bin/gcc-6 /usr/bin/gcc
gcc --version
sudo unlink /usr/bin/g++
sudo ln -s /usr/bin/g++-6 /usr/bin/g++
```
# Kaldi

First need to install Git. The most current version of Kaldi, possibly including unfinished and experimental features, can be downloaded by typing into a shell: 
```
git clone https://github.com/kaldi-asr/kaldi.git kaldi --origin upstream
cd kaldi
```
## The installation has two part.

### (1) go to tools/  and follow INSTALL instructions there.
```bash
# check dependencies
extras/check_dependencies.sh
# install dependencies for you need
# sudo apt install zlib1g-dev automake autoconf libtool subversion libatlas3-base
# if done will show: extras/check_dependencies.sh: all OK.

# 4 jobs
make -j 4 
# ........
# Warning: IRSTLM is not installed by default anymore. If you need IRSTLM
# Warning: use the script extras/install_irstlm.sh
# All done OK.

# install IRSTLM
./install_irstlm.sh
# .......
# ***() Installation of IRSTLM finished successfully
# ***() Please source the tools/extras/env.sh in your path.sh to enable it

# install SRILM
./install_srilm.sh
# Here need to download srilm then put the srilm.tgz in tools/
```

### (2)go to src/ and follow INSTALL instructions there.
```
./configure --shared
make depend -j 8
make -j 8
```
