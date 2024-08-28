#!/bin/bash
#docker run --rm -it -v $(pwd)/verticals:/var/lib/manatee/data/verticals -v $(pwd)/configuration-files:/var/lib/manatee/registry -p 8080:8080 -e CORPLIST=my_corpus acdhch/noske:5.66.3-2.223.6-open
docker run --rm -it -p 8080:8080 noske