echo -e "\nexport PATH=\$PATH:~/jailtoolkit/bin\n" >> ~/.zshrc
echo -e "\nalias siocage='sudo iocage'\n" >> ~/.zshrc
sudo pkg install -y py37-iocage
