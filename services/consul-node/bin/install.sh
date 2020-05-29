#!/usr/local/bin/zsh

if [ -z "$1" ] 
then
  echo ERROR: Missing argument for jail template
else
  main
fi

test()
{
  echo "Test works"
  ls -l
}

main()
{
  siocage="sudo iocage"
  $siocage exec $1 "git clone https://github.com/jhfoo/consulinstall.git"
  $siocage exec $1 "./consulinstall/bin/install.sh"
}
