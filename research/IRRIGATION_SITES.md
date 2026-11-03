# Sites for the irrigation scheme

Found by `tools/find_irrigation_sites.py` along the documented irrigation canals (research/RIVER_NETWORK.md): the primary canals of the Eridu region, the survey canals
between Uruk and Larsa and the channel network of Jotheri et al. 2018, only those 10 to 14 m wide (the model's canal is 10 m). The scheme needs 150 m along the canal and 94 m
across, no other canal or river inside, 200 m from any city, 150 m from the wall of Uruk, and where there are terrain rasters (the patch of Uruk) no water but its own
canal and a ground within 1.5 m. Metres are east (x) and south (z) of Uruk's tell; the bearing is that of the model's front (the scheme side).

Placed: `irrigation_works_uruk` (canal jotheri_176), `irrigation_works_eridu` (canal eridu_canal_105), `irrigation_works_larsa` (canal canal_w2).

264 sites at least 1.5 km apart (before the selection of the three), nearest to a city first:

| # | canal | width m | source | nearest city | city m | x | z | bearing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | eridu_canal_105 | 10 | eridu | eridu | 492 | 33353.7 | 55023.1 | 270.0 |
| 1 | eridu_canal_108 | 10 | eridu | eridu | 1196 | 34218.1 | 53788.7 | 180.0 |
| 2 | eridu_canal_050 | 10 | eridu | eridu | 1587 | 34204.4 | 56465.3 | 341.6 |
| 3 | eridu_canal_074 | 10 | eridu | eridu | 1588 | 35422.6 | 54871.6 | 274.4 |
| 4 | canal_w2 | 14 | survey | larsa | 1810 | 18883.3 | 5051.8 | 347.7 |
| 5 | jotheri_176 | 10 | jotheri2018 | uruk | 1878 | -345.2 | -1846.5 | 171.9 |
| 6 | eridu_canal_035 | 10 | eridu | eridu | 1902 | 32050.4 | 54264.4 | 242.1 |
| 7 | eridu_canal_068 | 10 | eridu | eridu | 1923 | 32358.7 | 56155.0 | 0.0 |
| 8 | jotheri_238 | 10 | jotheri2018 | larsa | 1963 | 20799.9 | 6016.5 | 65.8 |
| 9 | eridu_canal_061 | 10 | eridu | eridu | 2757 | 35967.3 | 53175.2 | 96.7 |
| 10 | eridu_canal_039 | 10 | eridu | eridu | 2850 | 35734.7 | 57047.1 | 57.7 |
| 11 | eridu_canal_014 | 10 | eridu | eridu | 3013 | 31912.1 | 52601.9 | 90.0 |
| 12 | jotheri_084 | 14 | jotheri2018 | uruk | 3059 | 1150.5 | -2834.5 | 109.7 |
| 13 | jotheri_165 | 14 | jotheri2018 | uruk | 3068 | -1167.5 | 2836.9 | 270.0 |
| 14 | eridu_canal_155 | 10 | eridu | eridu | 3072 | 36857.7 | 55471.7 | 180.0 |
| 15 | eridu_canal_062 | 10 | eridu | eridu | 3141 | 30714.3 | 55281.2 | 12.4 |
| 16 | eridu_canal_085 | 10 | eridu | eridu | 3422 | 30677.6 | 53602.5 | 204.1 |
| 17 | eridu_canal_034 | 10 | eridu | eridu | 3486 | 33288.1 | 51479.4 | 90.0 |
| 18 | jotheri_238 | 10 | jotheri2018 | larsa | 3491 | 21436.0 | 7430.0 | 65.8 |
| 19 | jotheri_005 | 14 | jotheri2018 | uruk | 3576 | 1657.1 | 3168.7 | 274.4 |
| 20 | eridu_canal_096 | 10 | eridu | eridu | 3927 | 32724.2 | 58688.3 | 243.7 |
| 21 | eridu_canal_126 | 10 | eridu | eridu | 3940 | 37697.7 | 54148.3 | 90.0 |
| 22 | jotheri_229 | 10 | jotheri2018 | uruk | 4221 | -974.7 | -4106.4 | 171.9 |
| 23 | eridu_canal_041 | 10 | eridu | eridu | 4228 | 37414.7 | 52671.7 | 96.8 |
| 24 | eridu_canal_083 | 10 | eridu | eridu | 4320 | 36404.8 | 58394.3 | 172.6 |
| 25 | eridu_canal_098 | 10 | eridu | eridu | 4522 | 30844.3 | 51529.6 | 330.5 |
| 26 | jotheri_040 | 14 | jotheri2018 | uruk | 4639 | -1362.2 | 4434.9 | 322.4 |
| 27 | eridu_canal_011 | 10 | eridu | eridu | 4727 | 33889.6 | 59648.5 | 63.6 |
| 28 | canal_c6 | 14 | survey | uruk | 4755 | 4242.2 | 2148.5 | 216.5 |
| 29 | jotheri_005 | 14 | jotheri2018 | uruk | 4780 | 1227.5 | 4619.5 | 330.9 |
| 30 | eridu_canal_130 | 10 | eridu | eridu | 4808 | 38614.6 | 55439.7 | 255.9 |
| 31 | eridu_canal_023 | 10 | eridu | eridu | 4840 | 37863.2 | 57605.7 | 0.0 |
| 32 | eridu_canal_067 | 10 | eridu | eridu | 4909 | 29415.3 | 52784.5 | 100.5 |
| 33 | jotheri_238 | 10 | jotheri2018 | larsa | 5032 | 22072.0 | 8843.5 | 65.8 |
| 34 | jotheri_043 | 10 | jotheri2018 | uruk | 5238 | 4403.4 | -2836.6 | 106.7 |
| 35 | jotheri_214 | 10 | jotheri2018 | larsa | 5298 | 15833.9 | 1432.5 | 90.0 |
| 36 | eridu_canal_092 | 10 | eridu | eridu | 5356 | 28546.4 | 54071.3 | 288.2 |
| 37 | eridu_canal_125 | 10 | eridu | eridu | 5440 | 36101.6 | 59867.9 | 309.0 |
| 38 | jotheri_218 | 10 | jotheri2018 | larsa | 5607 | 16514.9 | 8117.5 | 0.0 |
| 39 | eridu_canal_120 | 10 | eridu | eridu | 5674 | 39057.5 | 52705.0 | 134.9 |
