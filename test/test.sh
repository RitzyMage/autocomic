#!/bin/bash

ERROR='\033[0;31m'
SUCCESS='\033[0;32m'
RESET_COLOR='\033[0m' 

fail() {
    echo -e "${ERROR}TEST FAILED${RESET_COLOR}"
    echo "$1 and $2 did not match; exiting"
    exit 1
}

pdfInfo() {
    sed -e "/CreationDate/d" -e "/ModDate/d" -e "/\/ID/d" $1
}

compare() {
    return $(cmp -b <(pdfInfo $1) <(pdfInfo $2))
}

#usage: testComic $comicName $ymlFile $expectedResult
testComic() {
    echo "testing $3"
    rootDir="$(pwd)"
    mkdir $1
    cd $1
    cp "$rootDir/$2" comic.yml
    comic
    echo "comparing $rootDir/$3 with" *.pdf
    compare "$rootDir/$3" *.pdf  || fail "$rootDir/$3" *.pdf
    cleanupComic
    rm comic.yml
    cd ..
    rmdir $1
}
    
testComic overTheWall over-the-wall.yml OverTheWall.pdf

# TODO image splitting (vertical)
# TODO image splitting (horizontal)
# TODO image splitting (horizontal + vertical) (?)
# TODO comics with mouseover text and titles
# TODO comics with chapters
# TODO running javascript
# TODO using regex instead of CSS selectors
# TODO a comic that has pages with no images
# TODO a comic with multiple images per page

# TODO wait for script output and stop with SIGINT

echo -e "\n${SUCCESS}ALL TESTS PASSED${RESET_COLOR}"