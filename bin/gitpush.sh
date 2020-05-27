if [ -z "$1" ] 
then
  echo ERROR: Missing argument for commit message
else
  git add .
  git commit -m "$1"
  git push
fi


