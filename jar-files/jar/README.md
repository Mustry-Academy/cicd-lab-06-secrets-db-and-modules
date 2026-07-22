# jar-files/jar/

Library JARs that belong on the gateway classpath (`lib/core/gateway/`). They
load at **boot**, like modules — so the deploy step you add in Stretch S4
copies changed JARs into the container and restarts the gateway only when one
actually changed.

Pin exact versions and record where every JAR came from:

| JAR | Source | Checksum (sha256) |
|---|---|---|
| `commons-lang3-3.19.0.jar` | [Maven Central](https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.19.0/commons-lang3-3.19.0.jar) | `32733ab4bc90b45b63eb72677d886961003fd4ed113e07b1028f9877cb2ac735` |

Use it from any gateway-scoped script (Perspective bindings and transforms run
on the gateway, so the gateway classpath is the one that counts):

```python
from org.apache.commons.lang3 import StringUtils
flipped = StringUtils.reverse("Ignition")   # -> "noitingI"
```

The gateway has no package manager: this folder plus this table **is** the
lockfile. A JAR nobody can re-download and verify is a JAR you can't trust.
