#!/bin/bash
DOCCONF=fulldoc
mainDir=$PWD
docDir=doc/doxygen/${DOCCONF}/

remote="git@github.com:ECALELFS/EcalTiming.git"
if [ ! -d "${docDir}" ];then
    mkdir -p ${docDir}
fi

if [ ! -d "${docDir}/html" ];then
    cd ${docDir}
    git clone -b gh-pages  $remote html
    cd ${mainDir}
else
    cd ${docDir}/html
    if [ "`git branch | grep -c gh-pages`" == "0" ];then
	cd ${mainDir}
	rm ${docDir}/html/ -Rf
	cd ${docDir}/
	git clone -b gh-pages  $remote html
	cd ${mainDir}
    fi
fi


cd ${mainDir}
doxygen ${DOCCONF}

cd ${docDir}/html/
ls
git remote -v 
git branch 
git pull
git add *.html
git add *.css *.js
git add *.gif 
git add *.png
git add *.map
git add *.md5
git add search
git commit -m "updated documentation" -a
git commit -m "updated documentation" -a
git push origin gh-pages:gh-pages
cd -

