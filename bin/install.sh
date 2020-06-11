echo -e "\nexport PATH=\$PATH:~/jailtoolkit/bin" >> ~/.zshrc
PATH=$PATH:~/jailtoolkit/bin
echo -e "alias siocage='sudo iocage'" >> ~/.zshrc
alias siocage='sudo iocage'
sudo pkg install -y py37-iocage
