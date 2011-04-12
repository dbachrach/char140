#!bin/bash

i=5

echo "2"
while [$i -lte 9]
do
	./collider Ch rice $i -1 8
	i=${i + 2}
done

i=5

echo "4"
while [$i -lte 9]
do
	./collider Char rice $i -1 8
	i=${i + 2}
done

i=5

echo "2"
while [$i -lte 9]
do
	./collider CharlieS rice $i -1 8
	i=${i + 2}
done