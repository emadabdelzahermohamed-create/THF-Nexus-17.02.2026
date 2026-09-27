#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
if "THF_UPLOAD_KEYSTORE" in text:
    print("signing contract already present")
    raise SystemExit(0)

needle = "    buildTypes {\n        debug { applicationIdSuffix '.debug'; versionNameSuffix '-debug' }\n        release { minifyEnabled false; proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro' }\n    }"
replacement = """    signingConfigs {
        release {
            def ks = System.getenv('THF_UPLOAD_KEYSTORE')
            def storePass = System.getenv('THF_UPLOAD_STORE_PASSWORD')
            def alias = System.getenv('THF_UPLOAD_KEY_ALIAS')
            def keyPass = System.getenv('THF_UPLOAD_KEY_PASSWORD')
            if (!ks || !storePass || !alias || !keyPass) {
                throw new GradleException('THF production signing inputs are incomplete')
            }
            storeFile file(ks)
            storePassword storePass
            keyAlias alias
            keyPassword keyPass
        }
    }
    buildTypes {
        debug { applicationIdSuffix '.debug'; versionNameSuffix '-debug' }
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }"""
if needle not in text:
    raise SystemExit("expected RC2 buildTypes block not found; refusing to patch")
path.write_text(text.replace(needle, replacement), encoding="utf-8")
print("production signing contract applied")
