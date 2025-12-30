Lai šī pieeja nostrādātu, bija nepieciešams nedaudz izmainīt docker konfigurāciju.

Iekš `/lib/systemd/system/docker.service` faila bija jāizmaina `ExecStart` no:

```
ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

uz:

```
ExecStart=/usr/bin/dockerd --containerd=/run/containerd/containerd.sock
```

Paralēli tam ir jāizveido `/etc/docker/daemon.json` fails un tajā ir jāieraksta:

```
{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
```

Kad tas izdarīts, ir jāpalaiž:

```
systemctl daemon-reload
systemctl restart docker
```

Šis hosts parametrs ir nepieciešams, lai būtu iespējams izveidot tuneli no github
uz docker.

Alternatīva ir kopēt failus pa tiešo uz servera, slēgties klāt caur SSH un palaist
konfigurāciju šādā veidā. Man vairāk patīk šis variants.

Ja veic apt upgrade, tad ir jāveic atkārtotas darbības failā: `/lib/systemd/system/docker.service`

docker network inspect cloudflare-tunnel | grep Name