for customxml in $(ls output/*.xml);
	do xml=$(echo $customxml | sed 's/output\///');
	echo $xml;
	gtxml=$(ls Train/*.xml | grep $xml);
	echo $gtxml;
	outputxml="processed-xmls/$xml";
	echo $outputxml;
	python write_gt_to_custom_lines.py $customxml $gtxml $outputxml;
done
