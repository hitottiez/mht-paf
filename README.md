# mht-paf

##

```
git clone --recursive https://github.com/hitottiez/mht-paf.git
cd mht-paf
cp env.default .env
docker-compose build
```

```
docker-compose ps
        Name             Command    State          Ports        
----------------------------------------------------------------
mht-paf_deepsort_1      /bin/bash   Up                          
mht-paf_mcf-tracker_1   /bin/bash   Up                          
mht-paf_tsn_1           /bin/bash   Up      0.0.0.0:8888->80/tcp
```