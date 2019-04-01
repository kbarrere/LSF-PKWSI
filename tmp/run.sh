python ../bb-processing/heuristic.py ../bb-processing/pages/* ../bb-processing/index_test-sf-125-033.idx ./index_test.idx --gaussian-shape
python ../convert-lines-to-page/index_lines2page.py index_test.idx index_test-page.idx --id-list-file INF/ID_test-page.lst 
awk 'BEGIN{while (getline < "INF/ID_test-page.lst" > 0) L[$1]=""; while (getline < "index_test-page.idx" > 0) {k=$1"%"$2; S[k]=$3; G[k]=0}}{if ($2 in L) for (i=7;i<=NF;i++) if (length($i)>1) { k=$2"%"$i; G[k]=1; if (!(k in S)) S[k]=-1.0; } }END{for (k in S) print gensub("%"," ","g",k),G[k],S[k]}' INF/GT-page.txt > data_test-page.dat
kws-assessment -a -m -t -s data_test-page.dat -w INF/keywords_test.lst
