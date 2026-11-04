#!/bin/sh
# Im Ordner abluft-teile ausführen (benötigt git + gh, `gh auth login` vorher)
git init -b main
git add .
git commit -m "Abluft-Teile: Adapter, Rohr, Wartungsdeckel, Y-Stück"
gh repo create abluft-teile --public --source=. --push
