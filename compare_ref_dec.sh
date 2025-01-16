# FRAMERATE=(30 40 50 60 70 80 90 100 110 120 130 140 150 160 165) 

# BITRATES=(500 1000 2000 4000 8000 16000 32000) 
BITRATES=(4000) 

for bitrate in "${BITRATES[@]}"
do
    echo "Processing bitrate: $bitrate"

    python /c/Users/15142/Desktop/VRR/VRRML_Data/get_patchJOD.py $bitrate >  "04-21/${bitrate}Mbps.txt"
    # python /c/Users/15142/Desktop/VRR/VRR_cvvdp/compare_dec_ref.py $framerate
    # plot excel file: C:\Users\15142\Desktop\VRR_Plot
    wait
done



# run using git bash
# C:/Users/15142/Desktop/VRR/VRRML_data
