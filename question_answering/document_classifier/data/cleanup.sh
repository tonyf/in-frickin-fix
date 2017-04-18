for filename in *.txt; do
    for ((i=0; i<=3; i++)); do
	iconv -f utf-8 -t utf-8 -c "$filename" > "$filename"
    done
done
