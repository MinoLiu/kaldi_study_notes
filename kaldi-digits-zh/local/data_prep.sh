#!/bin/bash

waves_path=waves_digits

dict_path=data/local/dict

for path in "train" "test"; do
	speakerIDs=$(ls $waves_path/$path)
	for num in ${speakerIDs[@]}; do
		echo "$num m" >> data/$path/spk2gender
		waves=$(ls $waves_path/$path/$num)
		for wav in ${waves[@]}; do
			# wav.scp
			id=$(echo ${wav} | cut -d. -f1)
		  	echo "$id $waves_path/$path/$num/$wav" >> data/$path/wav.scp
			
			# text generator +_replace
			trans=$(for i in $(seq 2 $((${#id}-1))); do echo ${id:$i:1}_replace; done)
			echo "$id "${trans[@]}"" >> data/$path/text

			# utt2spk
			echo "$id $num" >> data/$path/utt2spk
		done
	done
	sed -i "s/0_replace/零/g" data/$path/text
	sed -i "s/1_replace/一/g" data/$path/text
	sed -i "s/2_replace/二/g" data/$path/text
	sed -i "s/3_replace/三/g" data/$path/text
	sed -i "s/4_replace/四/g" data/$path/text
	sed -i "s/5_replace/五/g" data/$path/text
	sed -i "s/6_replace/六/g" data/$path/text
	sed -i "s/7_replace/七/g" data/$path/text
	sed -i "s/8_replace/八/g" data/$path/text
	sed -i "s/9_replace/九/g" data/$path/text
done
