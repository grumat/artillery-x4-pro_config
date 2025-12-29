py -3 gen_stats.py --data=.\data\probe_accuracy_0.json        --out=.\data\probe_accuracy_0.jpg        --title="Probe Accuracy: Standard" > Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_180.json      --out=.\data\probe_accuracy_180.jpg      --title="Probe Accuracy: Rotation" >> Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_slow.json     --out=.\data\probe_accuracy_slow.jpg     --title="Probe Accuracy: Rotation + Slow Motion" >> Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_slow_cap.json --out=.\data\probe_accuracy_slow_cap.jpg --title="Probe Accuracy: Rotation + Slow Motion + Filter" >> Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_filament.json --out=.\data\probe_accuracy_filament.jpg --title="Probe Accuracy: Rotation + Slow Motion + Filter + Filament" --alt >> Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_baolsen.json --out=.\data\probe_accuracy_baolsen.jpg --title="Probe Accuracy: Rotation + Slow Motion + Filter (2026)" --alt >> Results.txt
py -3 gen_stats.py --data=.\data\probe_accuracy_panasonic.json --out=.\data\probe_accuracy_panasonic.jpg --title="Probe Accuracy: Rotation + Slow Motion + Filter + Panasonic (2026)" --alt >> Results.txt
