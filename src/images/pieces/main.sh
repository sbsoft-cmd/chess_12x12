# ImageMagick
#for f in *.svg; do
#    convert "$f" "${f%.svg}.png"
#done

cd images/pieces/
for f in b*.svg; do
    inkscape "$f" --export-filename="${f%.svg}.png" -w 128 -h 128
done
