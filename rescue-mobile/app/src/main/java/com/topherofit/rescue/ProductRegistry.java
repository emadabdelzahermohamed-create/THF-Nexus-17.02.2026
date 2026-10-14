package com.topherofit.rescue;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

public final class ProductRegistry {
    public static final class Product {
        public final String key;
        public final String title;
        public final String packageId;

        Product(String key, String title, String packageId) {
            this.key = key;
            this.title = title;
            this.packageId = packageId;
        }
    }

    private static final Map<String, Product> ALL;
    static {
        LinkedHashMap<String, Product> map = new LinkedHashMap<>();
        put(map, "hub", "THF Hub", "com.topherofit.thf.core");
        put(map, "fitness", "THF Fitness", "com.topherofit.thf.pulse");
        put(map, "wave", "WAVE MAWJA", "com.topherofit.wave");
        put(map, "arena", "Arena", "com.topherofit.arena");
        put(map, "ruinsciv", "RuinsCiv", "com.topherofit.ruinsciv");
        put(map, "endciv", "EndCiv", "com.topherofit.endciv");
        put(map, "tokenops", "THF TokenOps", "com.topherofit.tokenops");
        put(map, "publisher", "THF Publisher", "com.topherofit.publisher");
        put(map, "vault", "THF Vault", "com.topherofit.thf.vault");
        ALL = Collections.unmodifiableMap(map);
    }

    private static void put(Map<String, Product> map, String key, String title, String packageId) {
        map.put(key, new Product(key, title, packageId));
    }

    public static Map<String, Product> all() { return ALL; }

    public static Product get(String key) {
        Product product = ALL.get(key);
        if (product == null) throw new IllegalArgumentException("Unknown product: " + key);
        return product;
    }

    private ProductRegistry() {}
}
