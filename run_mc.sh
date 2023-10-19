o2-analysis-lf-delta-analysis -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-bc-converter -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-timestamp -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-event-selection -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-track-propagation -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-trackselection -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-multiplicity-table -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-pid-tpc-base -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-pid-tpc-full -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-pid-tof-base -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000 | \
o2-analysis-pid-tof-full -b --configuration json://configuration_mc.json --shm-segment-size 750000000000 --aod-memory-rate-limit 50000000000
