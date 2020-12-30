#!/bin/bash

fail() {
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
    
echo "testing over the wall"
testComic overTheWall over-the-wall.yml OverTheWall.pdf
# test comics:
# a basic comic
# image splitting (vertical)
# image splitting (horizontal)
# image splitting (horizontal + vertical) (?)
# comics with mouseover text and titles
# comics with chapters
# running javascript
# using regex instead of CSS selectors
# a comic that has pages with no images
# a comic with multiple images per page


# wait for script output and stop with SIGINT