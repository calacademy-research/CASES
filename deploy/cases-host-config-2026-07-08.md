# cases host configuration capture — 2026-07-08

Captured from cases.calacademy.org (10.2.22.18) before in-place OS upgrade chain 24.10→26.04 LTS.
VM: VMware, 8 vCPU / 62G RAM / 49G disk, DMZ VLAN. Users: joe(1000) admin(1001) apache(1002) ibss-alt(1003), no AD.

## Container
```
image=apache-flask restart=unless-stopped
entrypoint=["/bin/sh","-c","/var/www/apache-flask/docker_start.sh"] cmd=["/bin/bash","-restart"]
ports={"80/tcp":[{"HostIp":"","HostPort":"80"}]}
binds:
  /home/joe/CASES/visualization:/var/www/apache-flask/app
  /home/joe/CASES/employment_by_sector_by_month:/var/www/apache-flask/employment_by_sector_by_month
  /home/joe/CASES/age_fracs:/var/www/apache-flask/age_fracs
  /home/joe/CASES/r:/var/www/apache-flask/r
  /home/joe/CASES/employment_by_sector_Feb2020://var/www/apache-flask/employment_by_sector_Feb2020

```
(Note: the double-slash in the employment_by_sector_Feb2020 bind is verbatim from the running container.)

## Rebuild
- Working image built from visualization/Dockerfile.works (see also install_julia.py, run_with_julia.sh).
- julia-1.10.4-linux-x86_64.tar.gz (166M) is NOT in git (GitHub size limit) — download from julialang.org or restore from Joe's workstation ~/backups/cases-migration/CASES-dir/.
- visualization/env/ is a venv — rebuild, do not restore.
- Full docker image safety copy: workstation ~/backups/cases-migration/apache-flask-image-2026-07-07.tar.gz

## Netplan (cloud-init generated)
```yaml
network:
    ethernets:
        ens192:
            addresses:
            - 10.2.22.18/24
            gateway4: 10.2.22.1
            nameservers:
                addresses:
                - 1.1.1.1
                - 1.0.0.1
    version: 2
```

## UFW
```
Status: active

To                         Action      From
--                         ------      ----
Apache                     ALLOW       Anywhere                  
OpenSSH                    ALLOW       Anywhere                  
10.2.22.18 5666            ALLOW       10.1.10.194               
10050/tcp                  ALLOW       10.4.90.123               
Apache (v6)                ALLOW       Anywhere (v6)             
OpenSSH (v6)               ALLOW       Anywhere (v6)             

```

## Crontabs
Stock only — no custom cron jobs on this box (verified 2026-07-08).

## Other services
CrowdSec client + firewall bouncer (ansible role crowdsec-client in ibss-ansible), Sophos (sophos-spl), Trellix (xagt), zabbix-agent2, ntpsec, unattended-upgrades.
