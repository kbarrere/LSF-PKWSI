eps=10

rm results/*

for idx in $(ls idx/*.idx);
	do echo $idx;
	page=$(echo $idx | sed 's/idx/pages/' | sed 's/idx/xml/');
	echo $page;
	res=$(echo $idx | sed 's/idx/results/');
	echo $res;
	python ../bb-processing/merge_bbxs_v3.py --eps $eps $idx $page $res;
done

cat results/* > results.idx

python ../convert-lines-to-page/indexv2_lines2page.py results.idx index_test-page.idx --id-list-file INF/ID_test-page.lst

awk 'BEGIN{while (getline < "INF/ID_test-page.lst" > 0) L[$1]=""; while (getline < "index_test-page.idx" > 0) {k=$1"%"$2; S[k]=$3; G[k]=0}}{if ($2 in L) for (i=7;i<=NF;i++) if (length($i)>1) { k=$2"%"$i; G[k]=1; if (!(k in S)) S[k]=-1.0; } }END{for (k in S) print gensub("%"," ","g",k),G[k],S[k]}' INF/GT-page.txt > data_test-page.dat

kws-assessment -a -m -t -s data_test-page.dat -w INF/keywords_test.lst
